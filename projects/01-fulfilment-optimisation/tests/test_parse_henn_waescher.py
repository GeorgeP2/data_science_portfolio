import shutil
from pathlib import Path

import pytest
from fulfilment_optimisation.domain import Layout, Location
from fulfilment_optimisation.parsers.henn_waescher import (
    InstanceName,
    load_all,
    load_henn_waescher,
    parse_name,
    read_settings,
)

from portfolio import ProjectPaths

FIXTURES = Path(__file__).parent / "fixtures" / "henn_waescher" / "MTCR_X"
INSTANCE = FIXTURES / "1l-3-45-0.txt"
RAW = ProjectPaths.from_file(__file__).raw / "henn_waescher" / "obsp_instances"


def test_parse_name():
    expected = InstanceName(setting=12, routing="l", n_orders=40, capacity=45)
    assert parse_name("12l-40-45-0") == expected
    with pytest.raises(ValueError):
        parse_name("sett12")


def test_settings_stop_at_seed_block():
    settings = read_settings(FIXTURES / "sett1.txt")
    assert settings["m_no_a_p_b"] == "45"
    assert len(settings) == 10


def test_fixture_instance():
    instance = load_henn_waescher(INSTANCE)
    assert instance.name == "MTCR_X/1l-3-45-0"
    assert instance.capacity == 45
    assert [order.size for order in instance.orders] == [2, 1, 3]
    assert [order.due_date for order in instance.orders] == [188.063, 95.5, 240.0]
    assert instance.layout == Layout(
        n_aisles=10,
        n_positions=45,
        location_length=1.0,
        aisle_spacing=5.0,
        end_offset=1.0,
        depot_offset=1.0,
    )
    assert instance.layout.aisle_length == 46


def test_aisle_index_counts_sides():
    first, _, third = load_henn_waescher(INSTANCE).orders
    assert first.locations == (Location(0, 0, side=0), Location(9, 44, side=1))
    # Indices 2 and 3 are the two sides of aisle 1.
    assert third.locations[:2] == (Location(1, 3, side=0), Location(1, 3, side=1))


def copy_fixture(tmp_path: Path, name: str = INSTANCE.name) -> Path:
    folder = tmp_path / "MTCR_X"
    folder.mkdir()
    shutil.copy(FIXTURES / "sett1.txt", folder)
    return Path(shutil.copy(INSTANCE, folder / name))


def test_article_count_mismatch_raises(tmp_path: Path):
    path = copy_fixture(tmp_path)
    path.write_text(path.read_text().replace("number of articles 1\t", "number of articles 2\t"))
    with pytest.raises(ValueError, match="header says 2"):
        load_henn_waescher(path)


def test_name_disagreeing_with_settings_raises(tmp_path: Path):
    path = copy_fixture(tmp_path, "1l-3-75-0.txt")
    with pytest.raises(ValueError, match="disagrees"):
        load_henn_waescher(path)


@pytest.mark.skipif(not RAW.is_dir(), reason="raw Henn & Wäscher data not downloaded")
def test_all_raw_instances_parse():
    instances = load_all(RAW)
    assert len(instances) == 96
    for instance in instances:
        name = parse_name(instance.name.split("/")[1])
        assert len(instance.orders) == name.n_orders
        assert name.n_orders in {20, 40, 60, 80}
        assert instance.capacity in {45, 75}
        assert (instance.layout.n_aisles, instance.layout.n_positions) == (10, 45)
