"""Pareto chart: distance saved against FCFS by solve-time budget, per solver and routing policy.

    PYTHONPATH=src python -m fulfilment_optimisation.report

Reads the budget sweep (``outputs/sweep_*.parquet``; the commands are in the README) and writes:

- ``reports/figures/pareto.png`` and ``pareto_dark.png``: the README's headline chart, in light and
  dark variants;
- ``docs/projects/p1-fulfilment-optimisation/results/pareto.md``: every plotted value as a table.

ALNS and CP-SAT use whatever budget they're given, so they are curves over the budgets (x is the
budget). FCFS, seed and savings don't use extra time, so each is one point at its median actual
solve time. The y value is the mean saving over instances, with a 95% bootstrap interval. The
Pareto frontier joins the points no faster point beats.

Colours are the dataviz reference palette's first four categorical slots (validated for adjacent
pairs in both modes), with a distinct marker per series so identity never rests on colour alone.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

from portfolio import ProjectPaths, get_logger, load_config
from portfolio.io import read_table
from portfolio.paths import REPO_ROOT
from portfolio.plotting import save_fig

log = get_logger(__name__)

RESULTS_DOC = REPO_ROOT / "docs" / "projects" / "p1-fulfilment-optimisation" / "results"
ANYTIME = ["alns", "cp_sat"]
CONSTRUCTIVE = ["savings", "seed"]
LABELS = {"alns": "ALNS", "cp_sat": "CP-SAT", "savings": "Savings", "seed": "Seed"}
MARKERS = {"alns": "o", "cp_sat": "s", "savings": "D", "seed": "^"}
ROUTERS = {"s_shape": "S-shape routing", "largest_gap": "Largest-gap routing"}


@dataclass(frozen=True)
class Theme:
    surface: str
    text: str
    secondary: str
    muted: str
    grid: str
    baseline: str
    series: dict[str, str]


LIGHT = Theme(
    surface="#fcfcfb",
    text="#0b0b0b",
    secondary="#52514e",
    muted="#898781",
    grid="#e1e0d9",
    baseline="#c3c2b7",
    series={"alns": "#2a78d6", "cp_sat": "#eb6834", "savings": "#1baf7a", "seed": "#eda100"},
)
DARK = Theme(
    surface="#1a1a19",
    text="#ffffff",
    secondary="#c3c2b7",
    muted="#898781",
    grid="#2c2c2a",
    baseline="#383835",
    series={"alns": "#3987e5", "cp_sat": "#d95926", "savings": "#199e70", "seed": "#c98500"},
)


def summarise(runs: pd.DataFrame, samples: int = 2000, seed: int = 0) -> pd.DataFrame:
    """One row per (router, solver, x): mean % saved vs FCFS with a 95% bootstrap interval.

    x is the budget for anytime solvers and the median solve time for constructive ones.
    """
    fcfs = (
        runs[runs.solver == "fcfs"].groupby(["instance", "router"]).distance.first().rename("fcfs")
    )
    df = runs[runs.solver.isin(ANYTIME + CONSTRUCTIVE)].join(fcfs, on=["instance", "router"])
    df["saved"] = 100 * (df.fcfs - df.distance) / df.fcfs
    rng = np.random.default_rng(seed)
    rows = []
    for (router, solver, budget), group in df.groupby(["router", "solver", "time_limit"]):
        per_instance = group.groupby("instance").saved.mean().to_numpy()
        boot = per_instance[rng.integers(0, len(per_instance), (samples, len(per_instance)))]
        anytime = solver in ANYTIME
        rows.append(
            {
                "router": router,
                "solver": solver,
                "x": budget if anytime else group.solve_time.median(),
                "x_is_budget": anytime,
                "saved": per_instance.mean(),
                "ci_low": np.percentile(boot.mean(1), 2.5),
                "ci_high": np.percentile(boot.mean(1), 97.5),
                "instances": len(per_instance),
            }
        )
    out = pd.DataFrame(rows)
    # Constructive solvers ignore the budget, so keep one point each (their first budget).
    out = out.sort_values(["router", "solver", "x"])
    keep = out.x_is_budget | ~out.duplicated(["router", "solver"])
    return out[keep].reset_index(drop=True)


def frontier(points: pd.DataFrame) -> pd.DataFrame:
    """Points no faster point beats: sorted by time, keep each new best saving."""
    best, rows = -np.inf, []
    for row in points.sort_values(["x", "saved"], ascending=[True, False]).itertuples():
        if row.saved > best:
            best = row.saved
            rows.append(row)
    return pd.DataFrame(rows)


def _seconds(x: float, _pos: object = None) -> str:
    if x >= 1:
        return f"{x:.3g} s"
    return f"{x * 1000:.3g} ms"


def plot(summary: pd.DataFrame, theme: Theme) -> plt.Figure:
    routers = [r for r in ROUTERS if r in set(summary.router)]
    with plt.rc_context(
        {
            "font.size": 10,
            "axes.facecolor": theme.surface,
            "figure.facecolor": theme.surface,
            "savefig.facecolor": theme.surface,
            "text.color": theme.text,
            "axes.labelcolor": theme.secondary,
            "xtick.color": theme.muted,
            "ytick.color": theme.muted,
            "axes.edgecolor": theme.baseline,
        }
    ):
        fig, axes = plt.subplots(
            1, len(routers), figsize=(11, 4.6), sharey=True, layout="constrained"
        )
        axes = np.atleast_1d(axes)
        for ax, router in zip(axes, routers, strict=True):
            data = summary[summary.router == router]
            ax.set_xscale("log")
            ax.grid(True, which="major", color=theme.grid, linewidth=0.75)
            ax.set_axisbelow(True)
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            ax.axhline(0, color=theme.baseline, linewidth=1)

            front = frontier(data)
            ax.step(
                front.x,
                front.saved,
                where="post",
                color=theme.secondary,
                linewidth=1,
                linestyle=(0, (4, 3)),
                zorder=1,
                label="Pareto frontier",
            )

            for solver in ANYTIME:
                part = data[data.solver == solver].sort_values("x")
                if part.empty:
                    continue
                color = theme.series[solver]
                ax.fill_between(part.x, part.ci_low, part.ci_high, color=color, alpha=0.15, lw=0)
                ax.plot(
                    part.x,
                    part.saved,
                    color=color,
                    linewidth=1.8,
                    marker=MARKERS[solver],
                    markersize=6.5,
                    markeredgecolor=theme.surface,
                    markeredgewidth=1.2,
                    solid_capstyle="round",
                    zorder=4 if solver == "alns" else 3,  # ALNS is the frontier series
                    label=LABELS[solver],
                )
            for solver in CONSTRUCTIVE:
                part = data[data.solver == solver]
                if part.empty:
                    continue
                ax.plot(
                    part.x,
                    part.saved,
                    linestyle="none",
                    color=theme.series[solver],
                    marker=MARKERS[solver],
                    markersize=9 if MARKERS[solver] == "^" else 8,
                    markeredgecolor=theme.surface,
                    markeredgewidth=1.2,
                    zorder=3,
                    label=LABELS[solver],
                )
                row = part.iloc[0]
                ax.annotate(
                    LABELS[solver],
                    (row.x, row.saved),
                    xytext=(0, 9),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                    color=theme.secondary,
                    fontsize=9,
                )

            # Direct end labels for the curves, unless they would collide (the legend covers it).
            ends = {
                s: data[data.solver == s].sort_values("x").iloc[-1]
                for s in ANYTIME
                if (data.solver == s).any()
            }
            if len(ends) < 2 or abs(ends["alns"].saved - ends["cp_sat"].saved) > 1.2:
                for solver, row in ends.items():
                    ax.annotate(
                        LABELS[solver],
                        (row.x, row.saved),
                        xytext=(8, 0),
                        textcoords="offset points",
                        va="center",
                        color=theme.secondary,
                        fontsize=9,
                    )

            ax.annotate(
                "FCFS baseline",
                (ax.get_xlim()[0], 0),
                xytext=(4, 4),
                textcoords="offset points",
                color=theme.muted,
                fontsize=8.5,
            )
            ax.set_title(ROUTERS[router], loc="left", fontsize=10.5, color=theme.text)
            ax.xaxis.set_major_formatter(FuncFormatter(_seconds))
        axes[0].set_ylabel("Walking distance saved vs FCFS (%)")
        axes[0].set_ylim(bottom=-1.5)

        n = int(summary.instances.max())
        handles, labels = axes[0].get_legend_handles_labels()
        order = [labels.index(LABELS[s]) for s in [*ANYTIME, *CONSTRUCTIVE] if LABELS[s] in labels]
        order.append(labels.index("Pareto frontier"))
        # The chart title is the legend's heading, so the two can't collide.
        legend = fig.legend(
            [handles[i] for i in order],
            [labels[i] for i in order],
            loc="outside upper left",
            ncol=len(order),
            frameon=False,
            fontsize=9,
            labelcolor=theme.secondary,
            title="What each extra millisecond buys",
            title_fontproperties={"size": 13, "weight": "bold"},
            alignment="left",
        )
        legend.get_title().set_color(theme.text)
        fig.supxlabel(
            "Solve time, log scale: the budget for ALNS and CP-SAT, the actual time for seed and "
            f"savings.\nMean over {n} Henn & Wäscher instances per routing policy; bands are 95% "
            "intervals.",
            x=0.01,
            ha="left",
            fontsize=9,
            color=theme.secondary,
            linespacing=1.6,
        )
    return fig


def table(summary: pd.DataFrame) -> str:
    lines = [
        "# Pareto data: distance saved vs FCFS by solve time",
        "",
        "Generated by `python -m fulfilment_optimisation.report`; the table view of "
        "`reports/figures/pareto.png`. Mean % walking distance saved against FCFS over the "
        "Henn & Wäscher instances, with a 95% bootstrap interval. For ALNS and CP-SAT the time is "
        "the budget; for seed and savings it's the median actual solve time.",
        "",
    ]
    for router in [r for r in ROUTERS if r in set(summary.router)]:
        part = summary[summary.router == router]
        lines += [
            f"## {ROUTERS[router]}",
            "",
            "| Solver | Time | Saved vs FCFS % (95% CI) | Pareto frontier |",
            "|---|---:|---|:---:|",
        ]
        front = set(map(tuple, frontier(part)[["solver", "x"]].itertuples(index=False)))
        for row in part.sort_values(["solver", "x"]).itertuples():
            on_front = "✓" if (row.solver, row.x) in front else ""
            lines.append(
                f"| {LABELS[row.solver]} | {_seconds(row.x)} | {row.saved:.1f} "
                f"({row.ci_low:.1f} to {row.ci_high:.1f}) | {on_front} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(sweep: Sequence[Path] | None = None) -> None:
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    files = sweep or sorted(paths.outputs.glob("sweep_*.parquet"))
    if not files:
        raise FileNotFoundError("no outputs/sweep_*.parquet; run the sweep in the README first")
    runs = pd.concat([read_table(f) for f in files], ignore_index=True)
    summary = summarise(runs, seed=cfg.seed)

    for theme, name in ((LIGHT, "pareto.png"), (DARK, "pareto_dark.png")):
        fig = plot(summary, theme)
        log.info("wrote %s", save_fig(fig, paths.figures / name))
        plt.close(fig)
    RESULTS_DOC.mkdir(parents=True, exist_ok=True)
    (RESULTS_DOC / "pareto.md").write_text(table(summary) + "\n")
    log.info("wrote %s", RESULTS_DOC / "pareto.md")


if __name__ == "__main__":
    main()
