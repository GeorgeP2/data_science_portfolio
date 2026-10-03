import numpy as np
import pandas as pd
import pytest
from fulfilment_optimisation.domain import Batch, Location, Order
from fulfilment_optimisation.generator import LayoutRanges, sample_layout
from fulfilment_optimisation.routing import LargestGap, Optimal, SShape

from portfolio import ProjectPaths, load_config

PATHS = ProjectPaths.from_file(__file__)
RANGES = LayoutRanges.from_config(load_config(PATHS.config).generator["layout"])


def test_same_seed_same_layout():
    a = sample_layout(RANGES, np.random.default_rng(3))
    b = sample_layout(RANGES, np.random.default_rng(3))
    assert a == b


def test_sizes_stay_in_range_and_cover_it():
    rng = np.random.default_rng(0)
    layouts = [sample_layout(RANGES, rng) for _ in range(2000)]
    aisles = {lay.n_aisles for lay in layouts}
    positions = {lay.n_positions for lay in layouts}
    assert min(aisles) == RANGES.aisles[0] and max(aisles) == RANGES.aisles[1]
    assert min(positions) == RANGES.locations_per_aisle[0]
    assert max(positions) == RANGES.locations_per_aisle[1]
    assert all(lay.location_length == RANGES.location_length for lay in layouts)


def test_generated_layouts_route_under_all_routers():
    rng = np.random.default_rng(1)
    routers = [SShape(), LargestGap(), Optimal()]
    for _ in range(200):
        layout = sample_layout(RANGES, rng)
        picks = {
            Location(int(rng.integers(layout.n_aisles)), int(rng.integers(layout.n_positions)))
            for _ in range(int(rng.integers(1, 30)))
        }
        batch = Batch((Order(0, tuple(picks)),))
        lengths = [router.route(batch, layout).length for router in routers]
        assert all(length > 0 for length in lengths)
        assert lengths[2] <= min(lengths[:2]) + 1e-9  # optimal is never longer


def test_invalid_ranges_rejected():
    with pytest.raises(ValueError, match="aisles"):
        LayoutRanges((5, 4), (5, 40), 1.0, 5.0, 1.0, 1.0)


PROFILE = PATHS.processed / "kit_instances.parquet"


@pytest.mark.skipif(not PROFILE.exists(), reason="KIT suite not flattened (parsers.kit)")
def test_config_ranges_match_the_kit_profile():
    instances = pd.read_parquet(PROFILE, columns=["n_aisles", "n_locations"])
    assert RANGES.aisles == (instances.n_aisles.min(), instances.n_aisles.max())
    assert RANGES.locations_per_aisle == (instances.n_locations.min(), instances.n_locations.max())
