"""Turn a named scenario and a seed into an ``Instance``.

    PYTHONPATH=src python -m fulfilment_optimisation.generator [seed]

Scenarios live in ``generator.scenarios`` in ``config.yaml``; each overrides ``baseline``. A seed
fixes everything: the layout, catalogue, arrivals, order sizes and due dates are all drawn from one
``numpy`` generator. Seeds are split into a development range and a held-out range
(``generator.development_seeds`` / ``held_out_seeds``); only T21's final numbers use held-out seeds.

Orders are numbered in arrival order and carry their ``arrival_time``, so FCFS batches them as they
arrived.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from typing import Any

import numpy as np

from fulfilment_optimisation.domain import Instance, Order
from fulfilment_optimisation.generator.layout import LayoutRanges, sample_layout
from fulfilment_optimisation.generator.order_arrivals import arrival_times, due_dates, line_counts
from fulfilment_optimisation.generator.sku_affinity import build_catalogue, draw_lines
from portfolio import ProjectPaths, get_logger, load_config

log = get_logger(__name__)


def scenario_settings(generator: Mapping[str, Any], name: str) -> dict[str, Any]:
    """``baseline`` with the named scenario's keys on top."""
    scenarios = generator["scenarios"]
    if name not in scenarios:
        raise ValueError(f"unknown scenario {name!r}; choose from {sorted(scenarios)}")
    return {**scenarios["baseline"], **(scenarios[name] or {})}


def is_held_out(generator: Mapping[str, Any], seed: int) -> bool:
    low, high = generator["held_out_seeds"]
    return low <= seed <= high


def generate_instance(generator: Mapping[str, Any], name: str, seed: int) -> Instance:
    """One shift of ``name`` with ``seed``. ``generator`` is the config's ``generator`` section."""
    settings = scenario_settings(generator, name)
    size = generator["order_sizes"][settings["order_size"]]
    rng = np.random.default_rng(seed)

    # A scenario can pin parts of the layout (e.g. Henn & Wäscher's 10 x 45).
    layout_ranges = {**generator["layout"], **settings.get("layout", {})}
    layout = sample_layout(LayoutRanges.from_config(layout_ranges), rng)
    catalogue = build_catalogue(
        layout,
        rng,
        popularity=settings["popularity"],
        storage_policy=settings["storage_policy"],
        cluster_size=settings["cluster_size"],
    )
    n = int(rng.poisson(settings["orders_per_shift"]))
    arrivals_cfg = dict(settings["arrivals"])
    arrivals = arrival_times(n, rng, arrivals_cfg.pop("process"), **arrivals_cfg)
    if "weights" in size:
        lines = line_counts(n, rng, size["lines"], size["weights"])
    else:
        low, high = size["lines"]
        lines = line_counts(n, rng, list(range(low, high + 1)))
    lines = np.minimum(lines, size["capacity"])  # an order must fit one tour
    due = due_dates(arrivals, rng, settings["due_dates"])

    orders = tuple(
        Order(
            id=i,
            locations=tuple(
                catalogue.locations[a]
                for a in draw_lines(catalogue, int(k), settings["affinity"], rng)
            ),
            due_date=float(d),
            arrival_time=float(t),
        )
        for i, (t, k, d) in enumerate(zip(arrivals, lines, due, strict=True))
    )
    tag = "held-out" if is_held_out(generator, seed) else "dev"
    return Instance(f"generated/{name}/{tag}/{seed}", layout, orders, int(size["capacity"]))


def describe(instance: Instance) -> dict[str, float]:
    """Order statistics used to tell scenarios apart."""
    arrivals = np.array([o.arrival_time for o in instance.orders])
    hours = np.bincount((arrivals // 3600).astype(int), minlength=8)
    sizes = np.array([o.size for o in instance.orders])
    slack = np.array([o.due_date - o.arrival_time for o in instance.orders])
    aisles = np.array([len({loc.aisle for loc in o.locations}) for o in instance.orders])
    multi = sizes > 1
    return {
        "orders": len(instance.orders),
        "peak_orders_per_hour": int(hours.max()),
        "mean_lines": float(sizes.mean()),
        "mean_aisles_visited": float(aisles.mean()),
        "multi_line_single_aisle_share": float((aisles[multi] == 1).mean()) if multi.any() else 0.0,
        "median_slack_s": float(np.median(slack)),
    }


def main() -> None:
    cfg = load_config(ProjectPaths.from_file(__file__).config)
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    for name in cfg.generator["scenarios"]:
        instance = generate_instance(cfg.generator, name, seed)
        stats = describe(instance)
        layout = instance.layout
        log.info(
            "%-20s %2d x %2d layout, capacity %d: %s",
            name,
            layout.n_aisles,
            layout.n_positions,
            instance.capacity,
            {k: round(v, 2) for k, v in stats.items()},
        )
