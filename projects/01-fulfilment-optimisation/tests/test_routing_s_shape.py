import itertools
import random

import pytest
from fulfilment_optimisation.domain import DEPOT, Batch, Layout, Location, Order, distance
from fulfilment_optimisation.routing import Router, SShape

# Same Henn & Wäscher layout as test_domain.py: aisle length 46 LU, aisles 5 LU apart.
HW = Layout(
    n_aisles=10,
    n_positions=45,
    location_length=1.0,
    aisle_spacing=5.0,
    end_offset=1.0,
    depot_offset=0.5,
)
ROUTER: Router = SShape()


def batch(*locations: Location) -> Batch:
    return Batch((Order(0, locations),))


def test_empty_batch():
    route = ROUTER.route(Batch(()), HW)
    assert route.length == 0
    assert route.stops == ()


@pytest.mark.parametrize(
    ("locations", "expected"),
    [
        # One pick is in-and-back: 2 * 0.5 depot + 2 * 1 into the aisle.
        ([Location(0, 0)], 3),
        # 2 * 0.5 + 2 * 15 across + 2 * 45 into the aisle.
        ([Location(3, 44)], 121),
        # Even count, both aisles walked in full: 1 + 2 * 20 + 2 * 46.
        ([Location(1, 5), Location(4, 30)], 133),
        # Odd count: aisles 0 and 2 in full, aisle 5 in-and-back to y = 11: 1 + 50 + 92 + 22.
        ([Location(0, 40), Location(2, 1), Location(5, 3), Location(5, 10)], 165),
    ],
)
def test_hand_calculated_lengths(locations, expected):
    assert ROUTER.route(batch(*locations), HW).length == expected


def test_single_pick_is_a_round_trip_to_it():
    loc = Location(6, 17)
    assert ROUTER.length([loc], HW) == 2 * distance(DEPOT, loc, HW)


def test_both_sides_of_an_aisle_count_once():
    one_side = ROUTER.length([Location(2, 8)], HW)
    assert ROUTER.length([Location(2, 8, side=0), Location(2, 8, side=1)], HW) == one_side


def test_stops_alternate_direction():
    b = batch(Location(1, 3), Location(1, 20), Location(4, 7), Location(4, 30))
    route = ROUTER.route(b, HW)
    assert route.stops == (Location(1, 3), Location(1, 20), Location(4, 30), Location(4, 7))


def random_batches(n: int, seed: int = 0):
    rng = random.Random(seed)
    for _ in range(n):
        picks = {
            Location(rng.randrange(HW.n_aisles), rng.randrange(HW.n_positions), rng.randrange(2))
            for _ in range(rng.randint(1, 30))
        }
        yield batch(*picks)


def test_route_visits_every_pick_and_matches_length():
    for b in random_batches(300):
        route = ROUTER.route(b, HW)
        assert set(route.stops) == b.locations
        assert len(route.stops) == len(b.locations)
        assert route.length == ROUTER.length(b.locations, HW)


def test_never_shorter_than_shortest_walk_through_stops():
    for b in random_batches(300, seed=1):
        route = ROUTER.route(b, HW)
        path = [DEPOT, *route.stops, DEPOT]
        shortest = sum(distance(a, c, HW) for a, c in itertools.pairwise(path))
        assert route.length >= shortest - 1e-9
