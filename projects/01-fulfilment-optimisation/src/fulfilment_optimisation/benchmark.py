"""Run every solver x router x instance x time limit x seed and summarise the results.

    PYTHONPATH=src python -m fulfilment_optimisation.benchmark

The grid is the ``benchmark`` section of ``config.yaml``. Each run writes one row to
``outputs/runs.parquet``; ``outputs/metrics.json`` holds per (solver, router, time limit)
summaries: mean distance, % distance saved against FCFS on the same instance and router, and
p50/p95 solve time.

Runs execute in a process pool, so a solver never shares an interpreter (or the GIL) with another
one being timed.
"""

from __future__ import annotations

import itertools
from collections.abc import Callable, Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass

import pandas as pd

from fulfilment_optimisation.domain import Instance
from fulfilment_optimisation.parsers.henn_waescher import load_all
from fulfilment_optimisation.routing import LargestGap, Router, SShape
from fulfilment_optimisation.solvers import FCFS, Deadline, Solver, check_feasible
from portfolio import ProjectPaths, get_logger, load_config, seed_everything
from portfolio.io import save_json, write_table

log = get_logger(__name__)

BASELINE = "fcfs"


def _fcfs(seed: int) -> Solver:
    return FCFS()


# Factories take the run's seed, so stochastic solvers can be seeded per run.
SOLVERS: dict[str, Callable[[int], Solver]] = {"fcfs": _fcfs}
ROUTERS: dict[str, Callable[[], Router]] = {"s_shape": SShape, "largest_gap": LargestGap}


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


def run_one(run: Run, solvers: dict[str, Callable[[int], Solver]] = SOLVERS) -> dict:
    solver = solvers[run.solver](run.seed)
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
    solvers: dict[str, Callable[[int], Solver]] = SOLVERS,
) -> pd.DataFrame:
    """Execute ``runs`` and return one row per run, in a stable order.

    ``workers=1`` runs in this process, which lets tests pass solvers that can't be pickled.
    """
    if workers == 1:
        rows = [run_one(run, solvers) for run in runs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            rows = list(pool.map(run_one, runs, itertools.repeat(solvers), chunksize=1))
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


def main() -> None:
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    seed_everything(cfg.seed)
    bench = cfg.benchmark

    instances: list[Instance] = []
    for name in bench.instance_sets:
        if name != "henn_waescher":
            raise ValueError(f"unknown instance set {name!r}")
        instances += load_all(paths.data / cfg.data.henn_waescher / "obsp_instances")

    runs = grid(instances, bench.solvers, bench.routers, bench.time_limits, bench.seeds)
    log.info("running %d runs on %d instances", len(runs), len(instances))
    results = run_grid(runs, workers=bench.workers)
    summary = summarise(results)

    write_table(results, paths.outputs / "runs.parquet")
    save_json(
        {"grid": dict(bench), "summary": summary.to_dict(orient="records")},
        paths.outputs / "metrics.json",
    )
    log.info("results\n%s", summary.to_markdown(index=False))


if __name__ == "__main__":
    main()
