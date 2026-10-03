import itertools
import random

import pytest
from fulfilment_optimisation.domain import DEPOT, Batch, Layout, Location, Order, distance
from fulfilment_optimisation.routing import LargestGap, Router, SShape
from fulfilment_optimisation.routing.base import picks_by_aisle

# Same Henn & Wäscher layout as test_domain.py: aisle length 46 LU, aisles 5 LU apart.
HW = Layout(
    n_aisles=10,
    n_positions=45,
    location_length=1.0,
    aisle_spacing=5.0,
    end_offset=1.0,
    depot_offset=0.5,
)
ROUTER: Router = LargestGap()
S_SHAPE = SShape()


def batch(*locations: Location) -> Batch:
    return Batch((Order(0, locations),))


def test_empty_batch():
    route = ROUTER.route(Batch(()), HW)
    assert route.length == 0
    assert route.stops == ()


@pytest.mark.parametrize(
    ("locations", "expected"),
    [
        # One aisle is in-and-back, as in S-shape: 2 * 0.5 + 2 * 15 across + 2 * 45 in.
        ([Location(3, 44)], 121),
        # Two aisles are both walked in full: 1 + 2 * 20 + 2 * 46.
        ([Location(1, 5), Location(4, 30)], 133),
        # Middle aisle 2 has picks at y = 2 and 41, so its largest gap is 39 and it costs
        # 2 * (46 - 39) = 14: 1 + 2 * 25 + 92 + 14.
        ([Location(0, 40), Location(2, 1), Location(2, 40), Location(5, 10)], 157),
        # One deep pick in the middle aisle (y = 45) is collected from the back: 2 * 1.
        ([Location(0, 40), Location(2, 44), Location(5, 10)], 145),
        # Dense middle aisles (y = 1, 23, 45) leave a largest gap of 22, so each costs
        # 2 * (46 - 22) = 48, more than a full walk: 1 + 2 * 30 + 92 + 2 * 48.
        (
            [Location(0, 5), Location(6, 5)]
            + [Location(a, p) for a in (2, 4) for p in (0, 22, 44)],
            249,
        ),
    ],
)
def test_hand_calculated_lengths(locations, expected):
    assert ROUTER.route(batch(*locations), HW).length == expected


def test_low_density_beats_s_shape_and_high_density_loses():
    sparse = [Location(0, 40), Location(2, 1), Location(2, 40), Location(5, 10)]
    assert ROUTER.length(sparse, HW) == 157 < S_SHAPE.length(sparse, HW) == 165
    dense = [Location(0, 5), Location(6, 5)] + [Location(a, p) for a in (2, 4) for p in (0, 22, 44)]
    assert ROUTER.length(dense, HW) == 249 > S_SHAPE.length(dense, HW) == 245


def test_stops_follow_back_then_front_cross_aisle():
    b = batch(Location(0, 40), Location(2, 1), Location(2, 40), Location(5, 10), Location(5, 30))
    assert ROUTER.route(b, HW).stops == (
        Location(0, 40),  # leftmost aisle, front to back
        Location(2, 40),  # middle aisle, above the gap, from the back
        Location(5, 30),  # rightmost aisle, back to front
        Location(5, 10),
        Location(2, 1),  # middle aisle, below the gap, from the front
    )


def midpoint_length(locations: list[Location], layout: Layout) -> float:
    """Like largest gap, but each middle aisle is split at its midpoint instead."""
    aisles = picks_by_aisle(locations)
    if len(aisles) <= 2:
        return ROUTER.length(locations, layout)
    half = layout.aisle_length / 2
    total = 2 * layout.depot_offset + 2 * layout.x(max(aisles)) + 2 * layout.aisle_length
    for picks in list(aisles.values())[1:-1]:
        ys = [layout.y(loc.position) for loc in picks]
        total += 2 * max((y for y in ys if y <= half), default=0)
        upper = [y for y in ys if y > half]
        total += 2 * (layout.aisle_length - min(upper)) if upper else 0
    return total


def random_batches(n: int, seed: int = 0):
    rng = random.Random(seed)
    for _ in range(n):
        picks = {
            Location(rng.randrange(HW.n_aisles), rng.randrange(HW.n_positions), rng.randrange(2))
            for _ in range(rng.randint(1, 30))
        }
        yield batch(*picks)


def test_route_visits_every_pick_and_matches_length():
    for b in random_batches(1000):
        route = ROUTER.route(b, HW)
        assert set(route.stops) == b.locations
        assert len(route.stops) == len(b.locations)
        assert route.length == ROUTER.length(b.locations, HW)


def test_bounds_on_random_batches():
    """Largest gap is no worse than the midpoint split (Hall, 1993), never shorter than the
    shortest walk through its own stops, and the same as S-shape with one or two pick aisles."""
    for b in random_batches(1000, seed=1):
        locations = list(b.locations)
        route = ROUTER.route(b, HW)
        assert route.length <= midpoint_length(locations, HW) + 1e-9

        path = [DEPOT, *route.stops, DEPOT]
        shortest = sum(distance(a, c, HW) for a, c in itertools.pairwise(path))
        assert route.length >= shortest - 1e-9

        if len(picks_by_aisle(locations)) <= 2:
            assert route.length == S_SHAPE.length(locations, HW)


def reference_length(locations, layout) -> float:
    """The original formula, built on ``split_at_largest_gap``, to check the fast path."""
    from fulfilment_optimisation.routing.largest_gap import split_at_largest_gap

    aisles = picks_by_aisle(locations)
    if not aisles:
        return 0.0
    last = max(aisles)
    total = 2 * layout.depot_offset + 2 * layout.x(last)
    if len(aisles) == 1:
        return total + 2 * layout.y(max(loc.position for loc in aisles[last]))
    total += 2 * layout.aisle_length
    for picks in list(aisles.values())[1:-1]:
        total += 2 * (layout.aisle_length - split_at_largest_gap(picks, layout)[2])
    return total


@pytest.mark.parametrize(
    "layout",
    [
        HW,
        Layout(
            n_aisles=7,
            n_positions=20,
            location_length=1.3,
            aisle_spacing=3.7,
            end_offset=0.6,
            depot_offset=2.0,
        ),
    ],
    ids=["henn_waescher", "irregular_spacing"],
)
def test_fast_length_matches_reference(layout):
    rng = random.Random(7)
    for _ in range(2000):
        picks = [
            Location(
                rng.randrange(layout.n_aisles), rng.randrange(layout.n_positions), rng.randrange(2)
            )
            for _ in range(rng.randint(1, 40))
        ]
        assert ROUTER.length(picks, layout) == pytest.approx(reference_length(picks, layout))
