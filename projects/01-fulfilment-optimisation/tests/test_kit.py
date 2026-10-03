import json
from pathlib import Path

import pandas as pd
import pytest
from fulfilment_optimisation import kit_profile
from fulfilment_optimisation.parsers.kit import (
    describe_path,
    flatten,
    instance_paths,
    read_instance,
)

from portfolio import ProjectPaths

RAW = ProjectPaths.from_file(__file__).raw / "kit" / "Instances"


def write_suite(root: Path) -> Path:
    """A miniature KIT suite: two OFAT settings and one LHS setting, one replication each."""
    storage = root / "Data_input" / "OFAT" / "Storage_assignment"
    storage.mkdir(parents=True)
    # 2 aisles (x) x 3 locations (y): the OFAT naming would call this "3x2".
    cells = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]
    (storage / "6_pick_nodes_3x2_random.json").write_text(
        json.dumps({str(a): [x, y] for a, (x, y) in enumerate(cells, start=1)})
    )
    lhs_storage = root / "Data_input" / "LHS" / "Storage_assignment"
    lhs_storage.mkdir(parents=True)
    (lhs_storage / "001_4_pick_nodes_4x1_A.json").write_text(
        json.dumps({str(a): [a, 1] for a in range(1, 5)})  # 4 aisles of 1 location
    )

    def meta(storage_path: str, arrival, due) -> dict:
        return {
            "layout": "../../../Data_input/OFAT/Layout/x.pkl",
            "storage_assignment": storage_path,
            "num_instances": 1,
            "exp_num_orders": 3,
            "max_simulation_time": 28800,
            "arrival_config": arrival,
            "num_articles_in_order_config": [
                "weighted",
                {"population": [1, 2], "weights": [0.8, 0.2]},
            ],
            "due_date_config": due,
            "article_config": ["random", {}],
            "storage_policy": ["random", {}],
        }

    orders = [
        {"order_id": 1, "items": {"1": 1}, "arrival_time": 10.0, "due_date": 28800},
        {"order_id": 2, "items": {"2": 1, "4": 1}, "arrival_time": 50.0, "due_date": 28800},
        {"order_id": 3, "items": {"6": 2}, "arrival_time": 130.0, "due_date": 28800},
    ]
    files = {
        # Standard case sits one folder shallower than the other OFAT settings.
        "Orders/OFAT/Standard_case/instance_1.json": meta(
            "../../../Data_input/OFAT/Storage_assignment/6_pick_nodes_3x2_random.json",
            ["exponential", {}],
            ["shift_end", {}],
        ),
        "Orders/OFAT/Stochasticity/wave_5_0.5_original_orders/instance_1.json": meta(
            "../../../../Data_input/OFAT/Storage_assignment/6_pick_nodes_3x2_random.json",
            "wave_5_0.5",
            ["shift_end", {}],
        ),
    }
    for relative, m in files.items():
        path = root / relative
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"meta": m, "orders": orders}))
    lhs = root / "Orders/LHS/paramset_01_layout4x1/instance_1.json"
    lhs.parent.mkdir(parents=True)
    lhs_orders = [
        {"order_id": 1, "items": {"1": 1, "4": 1}, "arrival_time": 5.0, "due_date": 125.0},
    ]
    lhs.write_text(
        json.dumps(
            {
                "meta": meta(
                    "../../../Data_input/LHS/Storage_assignment/001_4_pick_nodes_4x1_A.json",
                    ["wave", {"num_waves": 5, "stochasticity": 0.3}],
                    ["relative_to_arrival", {"offset_seconds": 120.0}],
                ),
                "orders": lhs_orders,
            }
        )
    )
    return root


@pytest.fixture
def suite(tmp_path: Path) -> Path:
    return write_suite(tmp_path / "Instances")


def test_paths_and_descriptions(suite):
    paths = instance_paths(suite)
    assert len(paths) == 3
    described = [describe_path(p, suite) for p in paths]
    assert {d["factor"] for d in described} == {"LHS", "Standard_case", "Stochasticity"}
    assert {d["instance"] for d in described} >= {
        "OFAT/Standard_case/1",
        "LHS/paramset_01_layout4x1/1",
    }


def test_read_instance_derives_layout_from_storage_coordinates(suite):
    row, columns = read_instance(suite / "Orders/OFAT/Standard_case/instance_1.json", suite)
    assert (row["n_aisles"], row["n_locations"], row["n_articles"]) == (2, 3, 6)
    assert columns["lines"] == [1, 2, 1]
    assert columns["units"] == [1, 2, 2]
    assert columns["aisles_visited"] == [1, 2, 1]  # articles 2 and 4 are in aisles 1 and 2
    assert row["interarrival_mean"] == pytest.approx(60.0)
    assert row["share_due_at_shift_end"] == 1.0

    lhs, _ = read_instance(suite / "Orders/LHS/paramset_01_layout4x1/instance_1.json", suite)
    assert (lhs["n_aisles"], lhs["n_locations"]) == (4, 1)
    assert lhs["due_type"] == "relative_to_arrival"
    assert lhs["slack_median"] == pytest.approx(120.0)


def test_string_arrival_config_is_parsed(suite):
    path = suite / "Orders/OFAT/Stochasticity/wave_5_0.5_original_orders/instance_1.json"
    row, _ = read_instance(path, suite)
    assert (row["arrival_type"], row["num_waves"], row["stochasticity"]) == ("wave", 5, 0.5)


# One LHS setting in the fixture, so the profile's correlations are undefined (NaN with a warning).
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_flatten_and_profile(suite, tmp_path):
    out = tmp_path / "processed"
    assert flatten(suite, out, workers=1) == (3, 7)
    orders = pd.read_parquet(out / "kit_orders.parquet")
    assert len(orders) == 7
    instances = pd.read_parquet(out / "kit_instances.parquet")
    table = kit_profile.profile(instances, kit_profile.repeat_share(out / "kit_orders.parquet"))
    assert {"aisles", "orders per shift (8 h)", "lines per order", "due date"} <= set(
        table.parameter
    )
    assert "| `layout` | aisles |" in kit_profile.to_markdown(table)


@pytest.mark.skipif(not RAW.is_dir(), reason="raw KIT suite not downloaded")
def test_full_suite_layout():
    paths = instance_paths(RAW)
    assert len(paths) == 13200
    row, _ = read_instance(
        RAW / "Orders/OFAT/Layout/layout_128_pick_nodes_32x4/instance_1.json", RAW
    )
    assert (row["n_aisles"], row["n_locations"]) == (4, 32)
