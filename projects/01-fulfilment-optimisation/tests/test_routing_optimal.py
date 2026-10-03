import itertools
import random
import time

import pytest
from fulfilment_optimisation.domain import DEPOT, Batch, Layout, Location, Order, distance
from fulfilment_optimisation.routing import LargestGap, Optimal, Router, SShape

# Same Henn & Wäscher layout as the other routing tests: aisle length 46 LU, aisles 5 LU apart.
HW = Layout(
    n_aisles=10,
    n_positions=45,
    location_length=1.0,
    aisle_spacing=5.0,
    end_offset=1.0,
    depot_offset=0.5,
)
IRREGULAR = Layout(
    n_aisles=6,
    n_positions=20,
    location_length=1.3,
    aisle_spacing=3.7,
    end_offset=0.6,
    depot_offset=2.0,
)
ROUTER: Router = Optimal()


def batch(locations) -> Batch:
    return Batch((Order(0, tuple(locations)),))


def random_picks(rng: random.Random, layout: Layout, max_picks: int) -> list[Location]:
    return [
        Location(
            rng.randrange(layout.n_aisles), rng.randrange(layout.n_positions), rng.randrange(2)
        )
        for _ in range(rng.randint(1, max_picks))
    ]


def brute_force(locations, layout: Layout) -> float:
    """Shortest closed walk from the depot through every pick, over all visiting orders."""
    points = sorted({Location(loc.aisle, loc.position) for loc in locations})
    best = float("inf")
    for order in itertools.permutations(points):
        path = [DEPOT, *order, DEPOT]
        best = min(best, sum(distance(a, b, layout) for a, b in itertools.pairwise(path)))
    return best


def test_empty_batch():
    route = ROUTER.route(Batch(()), HW)
    assert route.length == 0
    assert route.stops == ()


@pytest.mark.parametrize(
    ("locations", "expected"),
    [
        # One pick: in and back, 2 * 0.5 + 2 * 15 across + 2 * 45 deep.
        ([Location(3, 44)], 121),
        # Picks near the front of aisles 1 and 4: in and back from the front in each,
        # 1 + 2 * 20 across + 2 * 6 + 2 * 6, cheaper than walking either aisle in full.
        ([Location(1, 5), Location(4, 5)], 1 + 40 + 12 + 12),
    ],
)
def test_hand_calculated_lengths(locations, expected):
    assert ROUTER.route(batch(locations), HW).length == pytest.approx(expected)


@pytest.mark.parametrize("layout", [HW, IRREGULAR], ids=["henn_waescher", "irregular"])
def test_matches_brute_force(layout):
    rng = random.Random(0)
    for _ in range(300):
        picks = random_picks(rng, layout, max_picks=7)
        assert ROUTER.length(picks, layout) == pytest.approx(brute_force(picks, layout))


@pytest.mark.parametrize("layout", [HW, IRREGULAR], ids=["henn_waescher", "irregular"])
def test_never_longer_than_heuristics_and_route_is_valid(layout):
    rng = random.Random(1)
    for _ in range(500):
        b = batch(random_picks(rng, layout, max_picks=40))
        route = ROUTER.route(b, layout)
        heuristic = min(
            SShape().length(b.locations, layout), LargestGap().length(b.locations, layout)
        )
        assert route.length <= heuristic + 1e-9
        # The stops are every pick, and walking them in order costs exactly the optimum.
        assert set(route.stops) == b.locations
        assert len(route.stops) == len(b.locations)
        path = [DEPOT, *route.stops, DEPOT]
        walk = sum(distance(a, c, layout) for a, c in itertools.pairwise(path))
        assert walk == pytest.approx(route.length)
        assert route.length == pytest.approx(ROUTER.length(b.locations, layout))


def test_100_picks_under_10ms():
    rng = random.Random(2)
    picks = [Location(rng.randrange(10), rng.randrange(45)) for _ in range(100)]
    ROUTER.length(picks, HW)
    start = time.perf_counter()
    for _ in range(20):
        ROUTER.length(picks, HW)
    assert (time.perf_counter() - start) / 20 < 0.010
