import pandas as pd
import pytest
from fulfilment_optimisation.published import compare, improvement_over_savings, to_markdown

from portfolio import ProjectPaths

PATHS = ProjectPaths.from_file(__file__)


def runs() -> pd.DataFrame:
    rows = []
    for i, (savings, alns) in enumerate([(100.0, 90.0), (200.0, 190.0), (300.0, 300.0)]):
        for solver, distance in [("savings", savings), ("alns", alns)]:
            rows.append(
                {
                    "instance": f"i{i}",
                    "n_orders": 40,
                    "capacity": 45,
                    "router": "s_shape",
                    "time_limit": 1.0,
                    "seed": 0,
                    "solver": solver,
                    "distance": distance,
                }
            )
    return pd.DataFrame(rows)


def test_improvement_is_of_the_average_tour_length():
    ours = improvement_over_savings(runs(), ["alns"], samples=200, seed=0)
    assert len(ours) == 1
    # (600 - 580) / 600, not the mean of per-instance improvements.
    assert ours.ours_pct.iloc[0] == pytest.approx(100 * 20 / 600)
    assert ours.ci_low.iloc[0] <= ours.ours_pct.iloc[0] <= ours.ci_high.iloc[0]
    assert ours.instances.iloc[0] == 3


def test_compare_applies_tolerance_on_shared_classes_only():
    ours = improvement_over_savings(runs(), ["alns"], samples=50, seed=0)
    published = pd.DataFrame(
        [
            {
                "n_orders": 40,
                "capacity": 45,
                "routing": "s_shape",
                "method": "abhc",
                "improvement_pct": 4.0,
            },
            {
                "n_orders": 100,
                "capacity": 30,
                "routing": "s_shape",
                "method": "abhc",
                "improvement_pct": 4.2,
            },
        ]
    )
    table = compare(ours, published, "abhc", tolerance_pp=1.0)
    assert len(table) == 1
    assert table.diff_pp.iloc[0] == pytest.approx(100 * 20 / 600 - 4.0)
    assert table.within.iloc[0]  # 3.33 is within 1 pp of 4.0
    assert not compare(ours, published, "abhc", tolerance_pp=0.5).within.iloc[0]
    assert "1/1 classes within tolerance" in to_markdown(table, "abhc", 1.0)


def test_reference_table_covers_both_routings():
    published = pd.read_csv(PATHS.root / "references" / "henn_waescher_2010_improvements.csv")
    assert len(published) == 2 * 16 * 5
    assert set(published.method) == {"ls", "ils1", "ils2", "ts", "abhc"}
    averages = published.groupby(["routing", "method"]).improvement_pct.mean().round(1)
    # The papers' "Average" rows (Tables 9.2 and 9.5).
    assert averages["s_shape", "abhc"] == 4.6
    assert averages["largest_gap", "abhc"] == 4.6
    assert averages["s_shape", "ts"] == 4.1
