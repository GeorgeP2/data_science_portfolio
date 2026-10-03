"""Profile the KIT suite into the parameter ranges the generator (T18, T19) draws from.

    PYTHONPATH=src python -m fulfilment_optimisation.kit_profile

Reads ``data/processed/kit_instances.parquet`` (from ``parsers.kit``) and writes the profile table
to ``data/processed/kit_profile.csv`` and, for the record,
``docs/projects/p1-fulfilment-optimisation/results/kit_profile.md``. The plotting functions are used
by ``notebooks/01_kit_profile.ipynb``.

Each row is one generator parameter: the range the KIT settings span, the distribution family the
replications are consistent with, and the evidence for it. The 100 LHS settings sample the
continuous parameters (layout size, order rate, due-date offset, wave stochasticity) uniformly
over a range, so the range itself is the calibrated input; the OFAT settings add the discrete
alternatives (storage policies, lines-per-order mixes, due-date rules).
"""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from portfolio import ProjectPaths, get_logger
from portfolio.paths import REPO_ROOT

log = get_logger(__name__)

RESULTS_DOC = REPO_ROOT / "docs" / "projects" / "p1-fulfilment-optimisation" / "results"


def settings(instances: pd.DataFrame) -> pd.DataFrame:
    """One row per parameter setting: its configuration and replication averages."""
    first = ["design", "factor", "n_aisles", "n_locations", "exp_num_orders", "arrival_type",
             "stochasticity", "lines_config", "due_type", "due_config", "article_type",
             "article_config", "storage_policy", "shift_seconds"]  # fmt: skip
    mean = ["n_orders", "interarrival_cv", "arrivals_per_30min_cv", "mean_lines", "mean_units",
            "mean_aisles_visited", "slack_median", "share_due_at_shift_end"]  # fmt: skip
    grouped = instances.groupby("setting")
    out = grouped[first].first().join(grouped[mean].mean())
    out["orders_dispersion"] = grouped.n_orders.var() / grouped.n_orders.mean()
    return out


def _span(series: pd.Series, fmt: str = "{:g}") -> str:
    q = series.quantile([0, 0.5, 1]).to_numpy()
    return f"{fmt.format(q[0])} to {fmt.format(q[2])} (median {fmt.format(q[1])})"


def _lines_mix(config: str) -> str:
    parsed = json.loads(config)
    if "value" in parsed:
        return f"always {parsed['value']}"
    pairs = zip(parsed["population"], parsed["weights"], strict=True)
    return ", ".join(f"{n}: {w:g}" for n, w in pairs)


def repeat_share(orders_path) -> float:
    """Share of orders with more units than lines (the same article drawn twice)."""
    import pyarrow.compute as pc
    import pyarrow.parquet as pq

    table = pq.read_table(orders_path, columns=["lines", "units"])
    return float(pc.mean(pc.greater(table["units"], table["lines"]).cast("int8")).as_py())


def profile(instances: pd.DataFrame, repeats: float = float("nan")) -> pd.DataFrame:
    """The generator parameter table. ``repeats`` is ``repeat_share`` of the orders table."""
    s = settings(instances)
    lhs, ofat = s[s.design == "LHS"], s[s.design == "OFAT"]
    expo = s[s.arrival_type == "exponential"]
    wave = s[s.arrival_type == "wave"]
    ofat_wave = wave[wave.design == "OFAT"]
    offsets = lhs.due_config.map(lambda c: json.loads(c)["offset_seconds"])
    lines_mixes = sorted(set(s.lines_config))
    rows = [
        {
            "module": "layout",
            "parameter": "aisles",
            "kit_range": _span(s.n_aisles, "{:.0f}"),
            "family": "uniform integer",
            "evidence": f"the LHS design spans {lhs.n_aisles.min()}-{lhs.n_aisles.max()}, "
            "independently of aisle length "
            f"(r = {lhs[['n_aisles', 'n_locations']].corr().iloc[0, 1]:.2f})",
        },
        {
            "module": "layout",
            "parameter": "locations per aisle",
            "kit_range": _span(s.n_locations, "{:.0f}"),
            "family": "uniform integer",
            "evidence": f"the LHS design spans {lhs.n_locations.min()}-{lhs.n_locations.max()}",
        },
        {
            "module": "order_arrivals",
            "parameter": "orders per shift (8 h)",
            "kit_range": _span(s.exp_num_orders, "{:.0f}"),
            "family": "Poisson around the expected count",
            "evidence": "variance / mean of the 100 replication counts per setting: "
            f"{_span(s.orders_dispersion, '{:.2f}')}; 1 for Poisson, and ±0.28 is sampling "
            "noise at 100 replications",
        },
        {
            "module": "order_arrivals",
            "parameter": "arrival process",
            "kit_range": f"{len(expo)} settings Poisson, {len(wave)} with 5 waves "
            f"(stochasticity {wave.stochasticity.min():.2f}-{wave.stochasticity.max():.2f})",
            "family": "Poisson process, or 5 waves; calibrate wave strength on the OFAT settings",
            "evidence": f"inter-arrival CV {expo.interarrival_cv.mean():.2f} without waves. OFAT "
            f"waves: CV {_span(ofat_wave.interarrival_cv, '{:.2f}')}, rising with stochasticity "
            f"(r = {ofat_wave.stochasticity.corr(ofat_wave.interarrival_cv):.2f}). LHS waves: CV "
            f"{_span(lhs.interarrival_cv, '{:.2f}')}, unrelated to the recorded stochasticity "
            f"(r = {lhs.stochasticity.corr(lhs.interarrival_cv):.2f}) but tracking volume "
            f"(r = {lhs.exp_num_orders.corr(lhs.interarrival_cv):.2f})",
        },
        {
            "module": "order_arrivals",
            "parameter": "lines per order",
            "kit_range": "; ".join(_lines_mix(c) for c in lines_mixes),
            "family": "categorical over 1-3",
            "evidence": f"mean lines per setting {_span(s.mean_lines, '{:.2f}')}; "
            "every LHS setting uses weights 0.8 / 0.15 / 0.05",
        },
        {
            "module": "order_arrivals",
            "parameter": "units per line",
            "kit_range": "1",
            "family": "constant",
            "evidence": f"{repeats:.2%} of orders hold an article twice (quantity 2), mostly on "
            "the smallest layouts: lines look drawn with replacement",
        },
        {
            "module": "order_arrivals",
            "parameter": "due date",
            "kit_range": f"shift end, arrival + 600 s, arrival + 1800 s, a mix; LHS arrival + "
            f"{offsets.min():.0f} to {offsets.max():.0f} s",
            "family": "rule per setting; LHS offset uniform",
            "evidence": f"{(s.due_type == 'shift_end').sum()} settings due at shift end, "
            f"{(s.due_type == 'relative_to_arrival').sum()} relative to arrival, "
            f"{(s.due_type == 'weighted').sum()} mixed (80% shift end / 15% 1800 s / 5% 600 s)",
        },
        {
            "module": "sku_affinity",
            "parameter": "article popularity",
            "kit_range": "uniform, or ABC: 20 / 30 / 50% of articles take 80 / 15 / 5% of demand",
            "family": "uniform or three-class ABC",
            "evidence": f"{(s.article_type == 'random').sum()} settings uniform, "
            f"{(s.article_type == 'auto_grouped').sum()} ABC with the same classes",
        },
        {
            "module": "layout",
            "parameter": "storage policy",
            "kit_range": ", ".join(sorted(set(s.storage_policy))),
            "family": "one of four rules",
            "evidence": f"{(s.storage_policy == 'A_closest_to_depot').sum()} settings A-closest-to-"
            f"depot (all LHS), {(s.storage_policy == 'random').sum()} random, one each A-to-X/Y",
        },
        {
            "module": "order_arrivals",
            "parameter": "aisles visited per order",
            "kit_range": _span(s.mean_aisles_visited, "{:.2f}"),
            "family": "outcome, not an input",
            "evidence": "follows from lines per order and storage; used by T20's validity check",
        },
    ]
    table = pd.DataFrame(rows)
    table.attrs["n_settings"] = (len(s), len(ofat), len(lhs))
    table.attrs["n_replications"] = len(instances)
    return table


def to_markdown(table: pd.DataFrame) -> str:
    total, ofat, lhs = table.attrs["n_settings"]
    lines = [
        "# KIT suite profile: generator parameter ranges",
        "",
        "Generated by `python -m fulfilment_optimisation.kit_profile` from "
        f"{table.attrs['n_replications']:,} replications in {total} settings ({ofat} OFAT, "
        f"{lhs} LHS) of the KIT Manual Warehouse Order Picking benchmark (Barlang, Lehmann & "
        "Furmans, 2026, CC BY 4.0). Ranges are across settings.",
        "",
        "**KIT orders are small**: 1-3 lines with one unit each (mean 1.25), against 5-25 items in "
        "the Henn & Wäscher instances. The generator takes its order-size distribution as a "
        "parameter so both regimes can be produced (T19).",
        "",
        "| Module | Parameter | KIT range | Family | Evidence |",
        "|---|---|---|---|---|",
    ]
    for row in table.itertuples():
        lines.append(
            f"| `{row.module}` | {row.parameter} | {row.kit_range} | {row.family} "
            f"| {row.evidence} |"
        )
    return "\n".join(lines) + "\n"


# --- plots for the notebook ---


def plot_layouts(s: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=(6, 4.5))
    for design, marker in (("LHS", "o"), ("OFAT", "s")):
        part = s[s.design == design].drop_duplicates(["n_aisles", "n_locations"])
        ax.scatter(part.n_aisles, part.n_locations, marker=marker, s=28, label=design, alpha=0.8)
    ax.set_xlabel("Aisles")
    ax.set_ylabel("Pick locations per aisle")
    ax.set_title("Layouts in the KIT suite", loc="left")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(1, 1))
    return fig


def plot_arrivals(s: pd.DataFrame) -> Figure:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    wave = s[s.arrival_type == "wave"]
    for design, marker in (("LHS", "o"), ("OFAT", "s")):
        part = wave[wave.design == design]
        axes[0].scatter(part.stochasticity, part.interarrival_cv, s=24, marker=marker, label=design)
    axes[0].legend(frameon=False)
    axes[0].axhline(1, color="grey", linewidth=1)
    axes[0].set_xlabel("Wave stochasticity")
    axes[0].set_ylabel("Inter-arrival time CV")
    axes[0].set_title("Burstiness vs wave stochasticity (1 = Poisson)", loc="left")
    axes[1].hist(s.exp_num_orders, bins=20)
    axes[1].set_xlabel("Expected orders per 8 h shift")
    axes[1].set_ylabel("Settings")
    axes[1].set_title("Order volume", loc="left")
    return fig


def plot_order_sizes(instances: pd.DataFrame) -> Figure:
    shares = instances[["share_lines_1", "share_lines_2", "share_lines_3", "share_lines_4plus"]]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["1", "2", "3", "4+"], shares.mean().to_numpy(), width=0.6)
    ax.set_xlabel("Lines per order")
    ax.set_ylabel("Share of orders")
    ax.set_title("KIT orders are mostly single-line", loc="left")
    return fig


def plot_slack(s: pd.DataFrame) -> Figure:
    fig, ax = plt.subplots(figsize=(6, 4))
    relative = s[s.due_type == "relative_to_arrival"].slack_median
    ax.hist(relative, bins=np.linspace(0, relative.max() * 1.05, 25))
    ax.set_xlabel("Due date minus arrival (s)")
    ax.set_ylabel("Settings")
    ax.set_title("Due-date slack where due dates follow arrival", loc="left")
    return fig


def main() -> None:
    paths = ProjectPaths.from_file(__file__)
    instances = pd.read_parquet(paths.processed / "kit_instances.parquet")
    table = profile(instances, repeat_share(paths.processed / "kit_orders.parquet"))
    table.to_csv(paths.processed / "kit_profile.csv", index=False)
    RESULTS_DOC.mkdir(parents=True, exist_ok=True)
    (RESULTS_DOC / "kit_profile.md").write_text(to_markdown(table))
    log.info("wrote %s and %s", paths.processed / "kit_profile.csv", RESULTS_DOC / "kit_profile.md")


if __name__ == "__main__":
    main()
