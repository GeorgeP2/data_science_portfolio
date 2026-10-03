"""Do generated instances resemble the benchmarks? (T20)

    PYTHONPATH=src python -m fulfilment_optimisation.validity

Needs the flattened KIT suite (``parsers.kit``), the Henn & Wäscher instances, and the 1 s
benchmark results in ``outputs/runs.parquet``. Writes figures to ``reports/figures/validity_*.png``
and the comparison to ``docs/projects/p1-fulfilment-optimisation/results/generator_validity.md``.

Comparisons, with thresholds fixed in ``config.yaml`` (``validity``) before any were computed:

1. **KIT standard case**: lines per order and aisles visited per order, generated under the same
   setup (8 aisles x 16 articles, random storage, uniform popularity, 1-3 lines at 0.8/0.15/0.05)
   against KIT's 100 replications.
2. **Every KIT setting**: mean aisles visited per order, generated under each setting's layout,
   lines mix, popularity and storage policy, against KIT's.
3. **Henn & Wäscher**: lines per order, aisles visited per order and aisles visited per FCFS tour
   against the 48 capacity-45 instances, for two presets: ``henn_waescher_paper`` (the setup as
   their paper describes it; specified before this check) and ``henn_waescher_like`` (corrected to
   what the instance files contain, after this check found that order sizes run 4-24, not 5-25, and
   that class B fills two aisles, not three). Both are reported.
4. **Solver ranking**: mean distance saved against FCFS per solver on generated
   ``henn_waescher_like`` instances against the published instances.

Discrete distributions are compared by total variation distance (TVD) and, as a second measure in
the data's own units, the Wasserstein distance (W1).

Our slots are two-sided (two articles per position), so a KIT aisle of ``L`` articles becomes
``ceil(L / 2)`` positions: an odd ``L`` gains one article per aisle. Aisles visited doesn't depend
on articles per aisle under random storage, and only slightly under class-based storage.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from scipy.stats import spearmanr, wasserstein_distance

from fulfilment_optimisation.benchmark import grid, run_grid
from fulfilment_optimisation.domain import Instance, Layout
from fulfilment_optimisation.generator import generate_instance
from fulfilment_optimisation.generator.order_arrivals import line_counts
from fulfilment_optimisation.generator.sku_affinity import build_catalogue, draw_lines
from fulfilment_optimisation.parsers.henn_waescher import load_all
from fulfilment_optimisation.routing import SShape
from fulfilment_optimisation.solvers import FCFS, Deadline
from portfolio import ProjectPaths, get_logger, load_config
from portfolio.io import read_table
from portfolio.paths import REPO_ROOT
from portfolio.plotting import save_fig

log = get_logger(__name__)

RESULTS_DOC = REPO_ROOT / "docs" / "projects" / "p1-fulfilment-optimisation" / "results"
REFERENCE, GENERATED = "#2a78d6", "#eb6834"  # dataviz reference palette slots 1 and 2
SOLVER_ORDER = ["seed", "savings", "alns", "cp_sat"]


def tvd(a: Sequence[int], b: Sequence[int]) -> float:
    """Total variation distance between two samples of integers."""
    values = sorted(set(a) | set(b))
    pa = pd.Series(a).value_counts(normalize=True).reindex(values, fill_value=0)
    pb = pd.Series(b).value_counts(normalize=True).reindex(values, fill_value=0)
    return float(0.5 * (pa - pb).abs().sum())


def verdict(distance: float, settings: Mapping[str, Any]) -> str:
    if distance <= settings["tvd_match"]:
        return "match"
    if distance <= settings["tvd_close"]:
        return "close"
    return "mismatch"


def sample_orders(
    layout: Layout,
    rng: np.random.Generator,
    n: int,
    lines: Sequence[int],
    weights: Sequence[float] | None,
    popularity: str,
    storage_policy: str,
) -> list[tuple]:
    """``n`` orders (as location tuples) from the generator's catalogue and line draws."""
    catalogue = build_catalogue(layout, rng, popularity=popularity, storage_policy=storage_policy)
    counts = line_counts(n, rng, lines, weights)
    return [
        tuple(catalogue.locations[a] for a in draw_lines(catalogue, int(k), 0.0, rng))
        for k in counts
    ]


def aisles_visited(orders: Sequence[Sequence[Any]]) -> list[int]:
    return [len({loc.aisle for loc in order}) for order in orders]


def _kit_layout(n_aisles: int, n_locations: int) -> Layout:
    return Layout(n_aisles, math.ceil(n_locations / 2), 1.0, 5.0, 1.0, 1.0)


def _lines_mix(config: str) -> tuple[list[int], list[float] | None]:
    import json

    parsed = json.loads(config)
    if "value" in parsed:
        return [int(parsed["value"])], None
    return list(parsed["population"]), list(parsed["weights"])


# --- 1 and 2: KIT ---


def kit_standard_case(
    paths: ProjectPaths, rng: np.random.Generator, n: int
) -> dict[str, tuple[list[int], list[int]]]:
    orders = read_table(paths.processed / "kit_orders.parquet")
    kit = orders[orders.instance.str.startswith("OFAT/Standard_case/")]
    generated = sample_orders(
        _kit_layout(8, 16), rng, n, [1, 2, 3], [0.8, 0.15, 0.05], "uniform", "random"
    )
    return {
        "lines per order": (kit.lines.tolist(), [len(o) for o in generated]),
        "aisles visited per order": (kit.aisles_visited.tolist(), aisles_visited(generated)),
    }


def kit_settings(paths: ProjectPaths, rng: np.random.Generator, n: int) -> pd.DataFrame:
    instances = read_table(paths.processed / "kit_instances.parquet")
    settings = instances.groupby("setting").agg(
        design=("design", "first"),
        n_aisles=("n_aisles", "first"),
        n_locations=("n_locations", "first"),
        lines_config=("lines_config", "first"),
        article_type=("article_type", "first"),
        storage_policy=("storage_policy", "first"),
        kit=("mean_aisles_visited", "mean"),
    )
    generated = []
    for row in settings.itertuples():
        lines, weights = _lines_mix(row.lines_config)
        popularity = "uniform" if row.article_type == "random" else "abc"
        orders = sample_orders(
            _kit_layout(row.n_aisles, row.n_locations),
            rng,
            n,
            lines,
            weights,
            popularity,
            row.storage_policy,
        )
        generated.append(float(np.mean(aisles_visited(orders))))
    settings["generated"] = generated
    return settings


# --- 3 and 4: Henn & Wäscher ---


def fcfs_tour_aisles(instances: Sequence[Instance]) -> list[int]:
    tours = []
    for instance in instances:
        solution = FCFS().solve(instance, SShape(), Deadline.never())
        tours += [len({loc.aisle for loc in b.locations}) for b in solution.batches]
    return tours


def henn_waescher(
    paths: ProjectPaths, generator: Mapping[str, Any], seeds: Sequence[int], scenario: str
) -> tuple[dict[str, tuple[list[int], list[int]]], list[Instance]]:
    cfg = load_config(paths.config)
    published = [
        i
        for i in load_all(paths.data / cfg.data.henn_waescher / "obsp_instances")
        if i.capacity == 45
    ]
    generated = [generate_instance(generator, scenario, s) for s in seeds]
    pub_orders = [o.locations for i in published for o in i.orders]
    gen_orders = [o.locations for i in generated for o in i.orders]
    comparisons = {
        "lines per order": ([len(o) for o in pub_orders], [len(o) for o in gen_orders]),
        "aisles visited per order": (aisles_visited(pub_orders), aisles_visited(gen_orders)),
        "aisles visited per FCFS tour": (fcfs_tour_aisles(published), fcfs_tour_aisles(generated)),
    }
    return comparisons, generated


def ranking(
    generated: Sequence[Instance], published_runs: pd.DataFrame, time_limit: float, workers: int
) -> pd.DataFrame:
    """Mean % saved vs FCFS per solver and router, on generated and on published instances."""
    routers = ["s_shape", "largest_gap"]
    runs = run_grid(
        grid(generated, ["fcfs", *SOLVER_ORDER], routers, [time_limit], [0]), workers=workers
    )

    def saved(df: pd.DataFrame) -> pd.Series:
        fcfs = df[df.solver == "fcfs"].set_index(["instance", "router"]).distance
        rows = df[df.solver.isin(SOLVER_ORDER)].join(fcfs.rename("fcfs"), on=["instance", "router"])
        rows["saved"] = 100 * (rows.fcfs - rows.distance) / rows.fcfs
        return rows.groupby(["router", "solver"]).saved.mean()

    published = published_runs[
        published_runs.router.isin(routers) & (published_runs.time_limit == time_limit)
    ]
    return pd.DataFrame({"published": saved(published), "generated": saved(runs)}).reset_index()


# --- plots and write-up ---


def plot_pmf(name: str, reference: str, preset: str, a: Sequence[int], b: Sequence[int]) -> Figure:
    values = np.arange(min(min(a), min(b)), max(max(a), max(b)) + 1)
    pa = pd.Series(a).value_counts(normalize=True).reindex(values, fill_value=0)
    pb = pd.Series(b).value_counts(normalize=True).reindex(values, fill_value=0)
    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    width = 0.4
    ax.bar(values - width / 2, pa, width, color=REFERENCE, label=reference)
    ax.bar(values + width / 2, pb, width, color=GENERATED, label=f"Generated ({preset})")
    ax.set_xlabel(name.capitalize())
    ax.set_ylabel("Share")
    ax.set_title(f"{name.capitalize()}: {reference} vs generated", loc="left", fontsize=11)
    ax.legend(frameon=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    return fig


def plot_settings(settings: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=(5, 5))
    for design, marker, colour in (("LHS", "o", REFERENCE), ("OFAT", "s", GENERATED)):
        part = settings[settings.design == design]
        ax.scatter(part.kit, part.generated, marker=marker, s=26, color=colour, label=design)
    low = min(settings.kit.min(), settings.generated.min()) - 0.02
    high = max(settings.kit.max(), settings.generated.max()) + 0.02
    ax.plot([low, high], [low, high], color="#898781", linewidth=1)
    ax.set_xlim(low, high)
    ax.set_ylim(low, high)
    ax.set_xlabel("KIT: mean aisles visited per order")
    ax.set_ylabel("Generated: mean aisles visited per order")
    ax.set_title("One point per KIT setting", loc="left", fontsize=11)
    ax.legend(frameon=False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    return fig


def main() -> None:
    paths = ProjectPaths.from_file(__file__)
    cfg = load_config(paths.config)
    settings = cfg.validity
    dev_low = cfg.generator["development_seeds"][0]
    rng = np.random.default_rng(cfg.seed)

    rows = []
    kit = kit_standard_case(paths, rng, 20 * settings.orders_per_setting)
    seeds = range(dev_low + 100, dev_low + 100 + settings.ranking_instances * 4)
    hw_paper, _ = henn_waescher(paths, cfg.generator, seeds, "henn_waescher_paper")
    hw, generated = henn_waescher(paths, cfg.generator, seeds, "henn_waescher_like")
    sources = (
        ("KIT standard case", "baseline setup", kit),
        ("Henn & Wäscher", "henn_waescher_paper", hw_paper),
        ("Henn & Wäscher", "henn_waescher_like", hw),
    )
    for source, preset, comparisons in sources:
        for name, (a, b) in comparisons.items():
            distance = tvd(a, b)
            slug = f"validity_{preset.replace(' ', '_')}_{name.replace(' ', '_')}"
            save_fig(plot_pmf(name, source, preset, a, b), paths.figures / f"{slug}.png")
            plt.close("all")
            rows.append(
                {
                    "source": source,
                    "preset": preset,
                    "statistic": name,
                    "reference_mean": float(np.mean(a)),
                    "generated_mean": float(np.mean(b)),
                    "tvd": distance,
                    "w1": float(wasserstein_distance(a, b)),
                    "verdict": verdict(distance, settings),
                    "figure": f"{slug}.png",
                }
            )
    table = pd.DataFrame(rows)

    per_setting = kit_settings(paths, rng, settings.orders_per_setting)
    save_fig(plot_settings(per_setting), paths.figures / "validity_kit_settings.png")
    plt.close("all")
    mae = float((per_setting.generated - per_setting.kit).abs().mean())

    published_runs = read_table(paths.outputs / "runs.parquet")
    ranks = ranking(
        generated[: settings.ranking_instances],
        published_runs,
        settings.ranking_time_limit,
        cfg.benchmark.workers,
    )

    RESULTS_DOC.mkdir(parents=True, exist_ok=True)
    doc = write_up(table, per_setting, mae, ranks, settings)
    (RESULTS_DOC / "generator_validity.md").write_text(doc)
    log.info("wrote %s", RESULTS_DOC / "generator_validity.md")
    log.info("\n%s", table.drop(columns="figure").round(3).to_string(index=False))
    log.info("per-setting MAE %.3f; ranking\n%s", mae, ranks.round(2).to_string(index=False))


def write_up(
    table: pd.DataFrame,
    per_setting: pd.DataFrame,
    mae: float,
    ranks: pd.DataFrame,
    settings: Mapping[str, Any],
) -> str:
    figs = "../../../../projects/01-fulfilment-optimisation/reports/figures"
    lines = [
        "# Generator validity",
        "",
        "Generated by `python -m fulfilment_optimisation.validity`. Thresholds were fixed in "
        "`config.yaml` (`validity`) before any comparison was computed: total variation distance "
        f"(TVD) ≤ {settings['tvd_match']:g} is a match, ≤ {settings['tvd_close']:g} close, and "
        "above that a mismatch. W1 is the Wasserstein distance in the statistic's own units.",
        "",
        "## Distributions",
        "",
        "| Reference | Generated preset | Statistic | Reference mean | Generated mean | TVD | W1 "
        "| Verdict |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in table.itertuples():
        lines.append(
            f"| {row.source} | `{row.preset}` | [{row.statistic}]({figs}/{row.figure}) "
            f"| {row.reference_mean:.2f} | {row.generated_mean:.2f} | {row.tvd:.3f} "
            f"| {row.w1:.3f} | {row.verdict} |"
        )
    lines += [
        "",
        "`henn_waescher_paper` follows the setup as Henn & Wäscher's paper describes it and was "
        "specified before this check. It failed on aisles visited because the instance files "
        "differ from the paper: order sizes are uniform on 4-24, not 5-25, and class B (36% of "
        "demand) fills aisles 2-3, not 2-4, leaving class C seven aisles instead of six. "
        "`henn_waescher_like` was then corrected to the files. Both are reported; only the "
        "corrected preset is used for the solver ranking below.",
    ]
    within = mae <= settings["setting_mae_aisles"]
    signed = (
        (per_setting.generated - per_setting.kit)
        .groupby(per_setting.design)
        .agg(["mean", "min", "max"])
    )
    worst = per_setting.assign(err=(per_setting.generated - per_setting.kit).abs()).nlargest(
        3, "err"
    )
    lines += [
        "",
        "## Every KIT setting",
        "",
        f"Mean aisles visited per order, generated under each of the {len(per_setting)} KIT "
        "settings' own layout, lines mix, popularity and storage policy "
        f"([scatter]({figs}/validity_kit_settings.png)). Mean absolute error **{mae:.3f}** aisles "
        f"against a threshold of {settings['setting_mae_aisles']:g}: "
        f"{'within' if within else 'outside'} it.",
        "",
        "The error isn't random: generated minus KIT is "
        + "; ".join(
            f"{design} {row['mean']:+.3f} on average ({row['min']:+.3f} to {row['max']:+.3f})"
            for design, row in signed.iterrows()
        )
        + ". All LHS settings store A articles closest to the depot. The probable cause (not "
        "tested) is that our slots are two-sided, two articles per position, so class A packs "
        "into fewer aisles and generated orders visit slightly fewer of them. Largest gaps:",
        "",
        "| Setting | KIT | Generated |",
        "|---|---:|---:|",
    ]
    for name, row in worst.iterrows():
        lines.append(f"| {name} | {row.kit:.3f} | {row.generated:.3f} |")
    lines += [
        "",
        "## Solver ranking",
        "",
        "Mean % distance saved against FCFS at "
        f"{settings['ranking_time_limit']:g} s: the published Henn & Wäscher instances against "
        f"{settings['ranking_instances']} generated `henn_waescher_like` instances.",
        "",
        "| Routing | Solver | Published | Generated |",
        "|---|---|---:|---:|",
    ]
    for row in ranks.itertuples():
        lines.append(
            f"| {row.router} | {row.solver} | {row.published:.1f}% | {row.generated:.1f}% |"
        )
    for router, part in ranks.groupby("router"):
        rho = spearmanr(part.published, part.generated).statistic
        order_pub = " > ".join(part.sort_values("published", ascending=False).solver)
        order_gen = " > ".join(part.sort_values("generated", ascending=False).solver)
        lines += [
            "",
            f"**{router}**: Spearman rank correlation {rho:.2f}. Published: {order_pub}. "
            f"Generated: {order_gen}.",
        ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
