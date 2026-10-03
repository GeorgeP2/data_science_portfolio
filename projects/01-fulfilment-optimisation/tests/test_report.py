import pandas as pd
import pytest
from fulfilment_optimisation.report import DARK, LIGHT, frontier, plot, summarise, table


def runs() -> pd.DataFrame:
    rows = []
    for i, fcfs in enumerate([100.0, 200.0]):
        base = {"instance": f"i{i}", "router": "s_shape", "seed": 0}
        rows += [
            {**base, "solver": "fcfs", "time_limit": 1.0, "distance": fcfs, "solve_time": 1e-5},
            {
                **base,
                "solver": "seed",
                "time_limit": 1.0,
                "distance": 0.9 * fcfs,
                "solve_time": 5e-4,
            },
            {
                **base,
                "solver": "savings",
                "time_limit": 1.0,
                "distance": 0.8 * fcfs,
                "solve_time": 0.01,
            },
            {
                **base,
                "solver": "alns",
                "time_limit": 0.1,
                "distance": 0.82 * fcfs,
                "solve_time": 0.1,
            },
            {
                **base,
                "solver": "alns",
                "time_limit": 1.0,
                "distance": 0.75 * fcfs,
                "solve_time": 1.0,
            },
            {
                **base,
                "solver": "cp_sat",
                "time_limit": 1.0,
                "distance": 0.78 * fcfs,
                "solve_time": 0.9,
            },
        ]
    return pd.DataFrame(rows)


def test_summary_uses_budget_for_anytime_and_solve_time_for_constructive():
    s = summarise(runs(), samples=100).set_index(["solver", "x"])
    assert s.loc[("alns", 1.0), "saved"] == pytest.approx(25)
    assert s.loc[("alns", 0.1), "saved"] == pytest.approx(18)
    assert s.loc[("savings", 0.01), "saved"] == pytest.approx(20)
    assert s.loc[("seed", 5e-4), "saved"] == pytest.approx(10)
    assert "fcfs" not in s.index.get_level_values("solver")


def test_frontier_keeps_points_no_faster_point_beats():
    s = summarise(runs(), samples=100)
    front = frontier(s)
    # Seed, savings, then ALNS at 1 s; ALNS at 0.1 s (18%) loses to savings (20%), and CP-SAT
    # at 1 s (22%) to ALNS at 1 s (25%).
    assert list(zip(front.solver, front.x, strict=True)) == [
        ("seed", 5e-4),
        ("savings", 0.01),
        ("alns", 1.0),
    ]


def test_plot_and_table_render():
    s = summarise(runs(), samples=100)
    for theme in (LIGHT, DARK):
        fig = plot(s, theme)
        assert len(fig.axes) == 1
    md = table(s)
    assert "| ALNS | 1 s | 25.0" in md
    assert md.count("✓") == 3
