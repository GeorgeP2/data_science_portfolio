"""Compare benchmark results with Henn & Wäscher's published improvements over C&W(ii).

    PYTHONPATH=src python -m fulfilment_optimisation.published
    PYTHONPATH=src python -m fulfilment_optimisation.published --runs runs.parquet runs_long.parquet

No per-instance distances are published for the Henn & Wäscher instances. Their paper (FEMM working
paper 07/2010, Tables 9.2 and 9.5) reports, per class of orders x capacity x routing, each method's
improvement of the *average* tour length over C&W(ii):

    100 * (mean C&W(ii) distance - mean method distance) / mean C&W(ii) distance

on 40 randomly generated instances per class. Our instances come from the same generator (order
sizes 5-25, class-based storage, 10 aisles x 45 cells), so the same relative measure, with our
savings solver as C&W(ii), is comparable class by class. The classes we share are 40, 60 and 80
orders with capacity 45 or 75.

Reads one or more results files from ``outputs/`` (from ``benchmark``; default ``runs.parquet``),
and writes a markdown table to
``docs/projects/p1-fulfilment-optimisation/results/published_comparison.md``. The tolerance and
reference method come from the ``published`` section of ``config.yaml``.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

import numpy as np
import pandas as pd

from portfolio import ProjectPaths, get_logger, load_config
from portfolio.io import read_table
from portfolio.paths import REPO_ROOT

log = get_logger(__name__)

RESULTS_DOC = REPO_ROOT / "docs" / "projects" / "p1-fulfilment-optimisation" / "results"
CLASS = ["n_orders", "capacity", "router"]


def improvement_over_savings(
    runs: pd.DataFrame, solvers: list[str], samples: int, seed: int
) -> pd.DataFrame:
    """Per class, time limit and solver: improvement of the mean distance over savings, with a
    95% bootstrap interval over instances."""
    savings = (
        runs[runs.solver == "savings"]
        .groupby(["instance", "router"])
        .distance.first()
        .rename("savings_distance")
    )
    rows = []
    rng = np.random.default_rng(seed)
    ours = runs[runs.solver.isin(solvers)].join(savings, on=["instance", "router"])
    for (n, capacity, router, time_limit, solver), group in ours.groupby(
        [*CLASS, "time_limit", "solver"]
    ):
        # Average over seeds first, so each instance counts once.
        per_instance = group.groupby("instance")[["distance", "savings_distance"]].mean()
        base, dist = per_instance.savings_distance.to_numpy(), per_instance.distance.to_numpy()
        idx = rng.integers(0, len(base), size=(samples, len(base)))
        boot = 100 * (base[idx].mean(1) - dist[idx].mean(1)) / base[idx].mean(1)
        rows.append(
            {
                "n_orders": n,
                "capacity": capacity,
                "router": router,
                "time_limit": time_limit,
                "solver": solver,
                "instances": len(base),
                "ours_pct": 100 * (base.mean() - dist.mean()) / base.mean(),
                "ci_low": np.percentile(boot, 2.5),
                "ci_high": np.percentile(boot, 97.5),
            }
        )
    return pd.DataFrame(rows)


def compare(
    ours: pd.DataFrame, published: pd.DataFrame, method: str, tolerance_pp: float
) -> pd.DataFrame:
    """Join our improvements with the published ``method`` on the shared classes."""
    reference = published[published.method == method].rename(
        columns={"routing": "router", "improvement_pct": "published_pct"}
    )[[*CLASS, "published_pct"]]
    table = ours.merge(reference, on=CLASS, how="inner")
    table["diff_pp"] = table.ours_pct - table.published_pct
    table["within"] = table.diff_pp >= -tolerance_pp
    return table.sort_values(["solver", "time_limit", "router", "n_orders", "capacity"])


def to_markdown(table: pd.DataFrame, method: str, tolerance_pp: float) -> str:
    lines = [
        "# Distance results against Henn & Wäscher (2010)",
        "",
        "Generated from the benchmark results. To regenerate, from the project folder:",
        "",
        "```bash",
        "PYTHONPATH=src python -m fulfilment_optimisation.benchmark  # 1 s grid, about 1.5 min",
        "PYTHONPATH=src python -m fulfilment_optimisation.benchmark --solvers savings alns \\",
        "    --time-limits 10 60 --orders 40 60 80 --param alns.max_iterations=100000000 \\",
        "    --output runs_long.parquet  # about 20 min with 10 workers",
        "PYTHONPATH=src python -m fulfilment_optimisation.published \\",
        "    --runs runs.parquet runs_long.parquet",
        "```",
        "",
        f"Improvement of the average tour length over C&W(ii) savings, per class, against the "
        f"published `{method}` (ABHC*, their best method; FEMM 07/2010 Tables 9.2 and 9.5). "
        f"Pass if ours is no more than {tolerance_pp:g} percentage point below. Different "
        "instances from the same generator, so the 95% bootstrap interval shows the sampling "
        "noise in our class means.",
        "",
    ]
    for (solver, time_limit), part in table.groupby(["solver", "time_limit"], sort=False):
        passed = int(part.within.sum())
        lines += [
            f"## {solver}, {time_limit:g} s ({passed}/{len(part)} classes within tolerance)",
            "",
            "| Routing | Orders | Capacity | Instances | Ours % (95% CI) | Published % "
            "| Diff (pp) | |",
            "|---|---:|---:|---:|---|---:|---:|---|",
        ]
        for row in part.itertuples():
            lines.append(
                f"| {row.router} | {row.n_orders} | {row.capacity} | {row.instances} "
                f"| {row.ours_pct:.1f} ({row.ci_low:.1f} to {row.ci_high:.1f}) "
                f"| {row.published_pct:.1f} | {row.diff_pp:+.1f} | {'✅' if row.within else '❌'} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Compare results with Henn & Wäscher (2010).")
    parser.add_argument("--runs", nargs="+", default=["runs.parquet"], help="files under outputs/")
    args = parser.parse_args(argv)
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    settings = cfg.published
    runs = pd.concat([read_table(paths.outputs / name) for name in args.runs], ignore_index=True)
    published = pd.read_csv(paths.root / "references" / "henn_waescher_2010_improvements.csv")

    ours = improvement_over_savings(
        runs, list(settings.solvers), settings.bootstrap_samples, cfg.seed
    )
    table = compare(ours, published, settings.reference_method, settings.tolerance_pp)
    RESULTS_DOC.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DOC / "published_comparison.md"
    out.write_text(to_markdown(table, settings.reference_method, settings.tolerance_pp) + "\n")
    log.info("wrote %s", out)
    log.info(
        "\n%s",
        table[[*CLASS, "time_limit", "solver", "ours_pct", "published_pct", "diff_pp", "within"]]
        .round(2)
        .to_string(index=False),
    )


if __name__ == "__main__":
    main()
