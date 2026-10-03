"""Run every solver x router x instance x time limit x seed and summarise the results.

    PYTHONPATH=src python -m fulfilment_optimisation.benchmark
    PYTHONPATH=src python -m fulfilment_optimisation.benchmark --solvers savings alns \
        --time-limits 10 60 --orders 40 60 80 --param alns.max_iterations=100000000 \
        --output runs_long.parquet

Without flags, the grid is the ``benchmark`` section of ``config.yaml``; flags override parts of it
for one-off runs.

The grid is the ``benchmark`` section of ``config.yaml``. Each run writes one row to
``outputs/runs.parquet``; ``outputs/metrics.json`` holds per (solver, router, time limit)
summaries: mean distance, % distance saved against FCFS on the same instance and router, and
p50/p95 solve time.

Runs execute in a process pool, so a solver never shares an interpreter (or the GIL) with another
one being timed.
"""

from __future__ import annotations

import argparse
import itertools
from collections.abc import Iterable, Mapping, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from typing import Any

import pandas as pd

from fulfilment_optimisation.domain import Instance
from fulfilment_optimisation.parsers.henn_waescher import load_all
from fulfilment_optimisation.registry import ROUTERS, SOLVERS, SolverFactory
from fulfilment_optimisation.solvers import Deadline, check_feasible
from portfolio import ProjectPaths, get_logger, load_config, seed_everything
from portfolio.io import save_json, write_table

log = get_logger(__name__)

BASELINE = "fcfs"


@dataclass(frozen=True, slots=True)
class Run:
    instance: Instance
    solver: str
    router: str
    time_limit: float
    seed: int


def grid(
    instances: Iterable[Instance],
    solvers: Sequence[str],
    routers: Sequence[str],
    time_limits: Sequence[float],
    seeds: Sequence[int],
) -> list[Run]:
    return [
        Run(instance, solver, router, float(time_limit), seed)
        for instance, solver, router, time_limit, seed in itertools.product(
            instances, solvers, routers, time_limits, seeds
        )
    ]


def run_one(
    run: Run,
    solvers: Mapping[str, SolverFactory] = SOLVERS,
    params: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict:
    solver = solvers[run.solver](run.seed, (params or {}).get(run.solver, {}))
    router = ROUTERS[run.router]()
    solution = solver.solve(run.instance, router, Deadline.after(run.time_limit))
    check_feasible(run.instance, solution)
    return {
        "instance": run.instance.name,
        "n_orders": len(run.instance.orders),
        "capacity": run.instance.capacity,
        "solver": run.solver,
        "router": run.router,
        "time_limit": run.time_limit,
        "seed": run.seed,
        "distance": solution.total_distance,
        "n_batches": len(solution.batches),
        "solve_time": solution.solve_time,
        "finished": solution.finished,
    }


def run_grid(
    runs: Sequence[Run],
    workers: int = 1,
    solvers: Mapping[str, SolverFactory] = SOLVERS,
    params: Mapping[str, Mapping[str, Any]] | None = None,
) -> pd.DataFrame:
    """Execute ``runs`` and return one row per run, in a stable order.

    ``params`` maps a solver name to its keyword arguments (the ``solvers`` section of config.yaml).

    ``workers=1`` runs in this process, which lets tests pass solvers that can't be pickled.
    """
    if workers == 1:
        rows = [run_one(run, solvers, params) for run in runs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(
                pool.map(
                    run_one, runs, itertools.repeat(solvers), itertools.repeat(params), chunksize=1
                )
            )
    keys = ["instance", "solver", "router", "time_limit", "seed"]
    return pd.DataFrame(rows).sort_values(keys, ignore_index=True)


def summarise(runs: pd.DataFrame) -> pd.DataFrame:
    """Per (solver, router, time limit): distance, % saved vs FCFS and solve-time percentiles."""
    df = runs.copy()
    baseline = df[df.solver == BASELINE].groupby(["instance", "router"]).distance.first()
    if baseline.empty:
        df["saved_vs_fcfs_pct"] = float("nan")
    else:
        fcfs = df.join(baseline.rename("fcfs_distance"), on=["instance", "router"]).fcfs_distance
        df["saved_vs_fcfs_pct"] = 100 * (fcfs - df.distance) / fcfs

    grouped = df.groupby(["solver", "router", "time_limit"])
    summary = grouped.agg(
        runs=("distance", "size"),
        mean_distance=("distance", "mean"),
        mean_saved_vs_fcfs_pct=("saved_vs_fcfs_pct", "mean"),
        solve_time_p50_ms=("solve_time", lambda s: 1000 * s.quantile(0.5)),
        solve_time_p95_ms=("solve_time", lambda s: 1000 * s.quantile(0.95)),
        finished_share=("finished", "mean"),
    )
    return summary.reset_index().round(4)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the benchmark grid.")
    parser.add_argument("--solvers", nargs="+", help="override benchmark.solvers")
    parser.add_argument("--time-limits", nargs="+", type=float, help="override, in seconds")
    parser.add_argument("--orders", nargs="+", type=int, help="only instances with these sizes")
    parser.add_argument(
        "--param",
        action="append",
        default=[],
        help="solver parameter, e.g. alns.max_iterations=1e8",
    )
    parser.add_argument("--workers", type=int, help="override benchmark.workers")
    parser.add_argument("--output", default="runs.parquet", help="file name under outputs/")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = parse_args(argv)
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    seed_everything(cfg.seed)
    bench = cfg.benchmark
    solvers = args.solvers or bench.solvers
    time_limits = args.time_limits or bench.time_limits

    instances: list[Instance] = []
    for name in bench.instance_sets:
        if name != "henn_waescher":
            raise ValueError(f"unknown instance set {name!r}")
        instances += load_all(paths.data / cfg.data.henn_waescher / "obsp_instances")
    if args.orders:
        instances = [i for i in instances if len(i.orders) in args.orders]

    runs = grid(instances, solvers, bench.routers, time_limits, bench.seeds)
    log.info("running %d runs on %d instances", len(runs), len(instances))
    params = {name: dict(p) for name, p in cfg.solvers.items()}
    for override in args.param:
        key, value = override.split("=", 1)
        solver, name = key.split(".", 1)
        params.setdefault(solver, {})[name] = type(params.get(solver, {}).get(name, 0.0))(
            float(value)
        )
    results = run_grid(runs, workers=args.workers or bench.workers, params=params)
    summary = summarise(results)

    write_table(results, paths.outputs / args.output)
    if args.output == "runs.parquet":
        save_json(
            {"grid": dict(bench), "summary": summary.to_dict(orient="records")},
            paths.outputs / "metrics.json",
        )
    log.info("results\n%s", summary.to_markdown(index=False))


if __name__ == "__main__":
    main()
