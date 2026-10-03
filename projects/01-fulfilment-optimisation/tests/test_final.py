import pandas as pd
import pytest
from fulfilment_optimisation.domain import Instance, Layout, Location, Order
from fulfilment_optimisation.final import build, summarise, windows

from portfolio import ProjectPaths, load_config

CFG = load_config(ProjectPaths.from_file(__file__).config)
LAYOUT = Layout(4, 5, 1.0, 5.0, 1.0, 1.0)


def test_windows_split_by_arrival_and_keep_every_order():
    orders = tuple(
        Order(i, (Location(0, 0),), arrival_time=t) for i, t in enumerate([10, 1700, 1810, 5000])
    )
    instance = Instance("generated/x/held-out/10000", LAYOUT, orders, 5)
    parts = windows(instance, 1800)
    assert [[o.id for o in p.orders] for p in parts] == [[0, 1], [2], [3]]
    assert [p.name.rsplit("/", 1)[1] for p in parts] == ["w00", "w01", "w02"]  # empty w02.. dropped
    assert windows(instance, None) == [instance]


def test_final_seeds_are_held_out_and_disjoint_from_development():
    low, high = CFG.final["seeds"]
    held, dev = CFG.generator["held_out_seeds"], CFG.generator["development_seeds"]
    assert held[0] <= low <= high <= held[1]
    assert dev[1] < held[0]


def test_build_refuses_development_seeds():
    final = {**CFG.final, "seeds": [5, 5], "scenarios": ["henn_waescher_like"]}
    with pytest.raises(ValueError, match="held_out_seeds"):
        build(final, CFG.generator)


def test_summary_sums_windows_per_shift():
    rows = []
    for window, (fcfs, alns) in enumerate([(100.0, 80.0), (100.0, 90.0)]):
        for solver, d in (("fcfs", fcfs), ("alns", alns)):
            rows.append({"scenario": "baseline", "seed": 10000, "router": "s_shape",
                         "solver": solver, "instance": f"w{window}", "distance": d})  # fmt: skip
    summary = summarise(pd.DataFrame(rows), samples=10).set_index("solver")
    assert summary.loc["alns", "saved"] == pytest.approx(15.0)  # (200 - 170) / 200
    assert summary.loc["alns", "windows_per_shift"] == 2
