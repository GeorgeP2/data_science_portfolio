"""The held-out run (T21): every final scenario on held-out seeds, run once.

    PYTHONPATH=src python -m fulfilment_optimisation.final

Settings come from the ``final`` and ``solvers`` sections of ``config.yaml``, committed before the
run. Seeds come from ``generator.held_out_seeds``, which development never used.

A KIT-style shift has 1,000+ orders, too many to batch in one solve, so it is split into
``window_seconds`` arrival windows and each window is batched on its own, as a warehouse batching
every half hour would. The Henn & Wäscher-style scenarios (~60 orders) are batched whole. A
shift's distance is the sum over its windows.

Writes ``outputs/final_runs.parquet`` (one row per window x solver x router) and
``docs/projects/p1-fulfilment-optimisation/results/held_out.md``.
"""

from __future__ import annotations

import subprocess
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from fulfilment_optimisation.benchmark import grid, run_grid
from fulfilment_optimisation.domain import Instance
from fulfilment_optimisation.generator import generate_instance, is_held_out
from portfolio import ProjectPaths, get_logger, load_config
from portfolio.io import write_table
from portfolio.paths import REPO_ROOT

log = get_logger(__name__)

RESULTS_DOC = REPO_ROOT / "docs" / "projects" / "p1-fulfilment-optimisation" / "results"


def windows(instance: Instance, seconds: float | None) -> list[Instance]:
    """``instance`` split by arrival time into consecutive windows (empty windows dropped)."""
    if seconds is None:
        return [instance]
    by_window: dict[int, list] = {}
    for order in instance.orders:
        by_window.setdefault(int(order.arrival_time // seconds), []).append(order)
    return [
        Instance(f"{instance.name}/w{k:02d}", instance.layout, tuple(orders), instance.capacity)
        for k, orders in sorted(by_window.items())
    ]


def build(final: Mapping[str, Any], generator: Mapping[str, Any]) -> list[Instance]:
    low, high = final["seeds"]
    out = []
    for scenario in final["scenarios"]:
        for seed in range(low, high + 1):
            if not is_held_out(generator, seed):
                raise ValueError(f"seed {seed} is not in generator.held_out_seeds")
            instance = generate_instance(generator, scenario, seed)
            whole = scenario in final["whole_shift"]
            out += windows(instance, None if whole else final["window_seconds"])
    return out


def run(
    instances: Sequence[Instance], final: Mapping[str, Any], params: Mapping[str, Any]
) -> pd.DataFrame:
    single = [s for s in final["solvers"] if s != "cp_sat"]
    parts = [
        run_grid(
            grid(instances, single, final["routers"], [final["time_limit"]], [0]),
            workers=final["workers"],
            params=params,
        )
    ]
    if "cp_sat" in final["solvers"]:
        parts.append(
            run_grid(
                grid(instances, ["cp_sat"], final["routers"], [final["time_limit"]], [0]),
                workers=final["cp_sat_workers"],
                params=params,
            )
        )
    runs = pd.concat(parts, ignore_index=True)
    # instance names are generated/<scenario>/held-out/<seed>[/wNN]
    parts_ = runs.instance.str.split("/")
    runs["scenario"] = parts_.str[1]
    runs["seed"] = parts_.str[3].astype(int)
    return runs


def summarise(runs: pd.DataFrame, samples: int = 2000, seed: int = 0) -> pd.DataFrame:
    """Per scenario, router and solver: mean shift distance and % saved vs FCFS (95% interval)."""
    shifts = runs.groupby(["scenario", "seed", "router", "solver"], as_index=False).agg(
        distance=("distance", "sum"), windows=("instance", "nunique")
    )
    fcfs = shifts[shifts.solver == "fcfs"].set_index(["scenario", "seed", "router"]).distance
    shifts = shifts.join(fcfs.rename("fcfs"), on=["scenario", "seed", "router"])
    shifts["saved"] = 100 * (shifts.fcfs - shifts.distance) / shifts.fcfs
    rng = np.random.default_rng(seed)
    rows = []
    for (scenario, router, solver), g in shifts.groupby(["scenario", "router", "solver"]):
        saved = g.saved.to_numpy()
        boot = saved[rng.integers(0, len(saved), (samples, len(saved)))].mean(1)
        rows.append(
            {
                "scenario": scenario,
                "router": router,
                "solver": solver,
                "shifts": len(g),
                "windows_per_shift": float(g.windows.mean()),
                "mean_distance": float(g.distance.mean()),
                "saved": float(saved.mean()),
                "ci_low": float(np.percentile(boot, 2.5)),
                "ci_high": float(np.percentile(boot, 97.5)),
            }
        )
    return pd.DataFrame(rows)


def _cell(row: pd.Series) -> str:
    return f"{row['saved']:.1f}% ({row['ci_low']:.1f}-{row['ci_high']:.1f})"


def to_markdown(summary: pd.DataFrame, final: Mapping[str, Any], commit: str) -> str:
    solvers = [s for s in final["solvers"] if s != "fcfs"]
    lines = [
        "# Held-out results",
        "",
        "Generated by `python -m fulfilment_optimisation.final`, run once on commit "
        f"`{commit}` with the `final` and `solvers` settings in `config.yaml` as committed there. "
        f"Seeds {final['seeds'][0]}-{final['seeds'][1]} (held out: never used in development), "
        f"{final['time_limit']:g} s per batching window. KIT-style scenarios are batched per "
        f"{final['window_seconds'] // 60:g}-minute arrival window and summed over the shift; "
        "Henn & Wäscher-style ones are batched whole. Values are mean % walking distance saved "
        "against FCFS (same routing) over the shifts, with a 95% bootstrap interval.",
        "",
        "`tight_due_dates` isn't run: it changes only due dates, which these distance-minimising "
        "solvers ignore, so its results would repeat `baseline`'s.",
    ]
    for router in final["routers"]:
        part = summary[summary.router == router]
        lines += [
            "",
            f"## {router.replace('_', '-')} routing",
            "",
            "| Scenario | Windows per shift | FCFS distance | "
            + " | ".join(
                s.replace("_", "-").upper() if s == "cp_sat" else s.capitalize() for s in solvers
            )
            + " |",
            "|---|---:|---:|" + "---:|" * len(solvers),
        ]
        for scenario in final["scenarios"]:
            rows = part[part.scenario == scenario].set_index("solver")
            if rows.empty:
                continue
            cells = [_cell(rows.loc[s]) for s in solvers]
            best = max(solvers, key=lambda s: rows.loc[s, "saved"])
            cells[solvers.index(best)] = f"**{cells[solvers.index(best)]}**"
            lines.append(
                f"| `{scenario}` | {rows.loc['fcfs', 'windows_per_shift']:.0f} "
                f"| {rows.loc['fcfs', 'mean_distance']:,.0f} | " + " | ".join(cells) + " |"
            )
    return "\n".join(lines) + "\n"


def main() -> None:
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    final = cfg.final
    commit = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--", str(paths.config)], capture_output=True, text=True
    ).stdout.strip()
    if dirty:
        raise SystemExit("config.yaml has uncommitted changes; commit the settings before the run")

    instances = build(final, cfg.generator)
    log.info("%d batching windows across %d scenarios", len(instances), len(final["scenarios"]))
    params = {name: dict(p) for name, p in cfg.solvers.items()}
    runs = run(instances, final, params)
    write_table(runs, paths.outputs / "final_runs.parquet")
    summary = summarise(runs, seed=cfg.seed)
    RESULTS_DOC.mkdir(parents=True, exist_ok=True)
    (RESULTS_DOC / "held_out.md").write_text(to_markdown(summary, final, commit))
    log.info("wrote %s", RESULTS_DOC / "held_out.md")


if __name__ == "__main__":
    main()
