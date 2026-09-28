import itertools
import random

import pytest
from fulfilment_optimisation.domain import (
    DEPOT,
    Batch,
    Instance,
    Layout,
    Location,
    Order,
    distance,
)

# Henn & Wäscher (2012), section 6.1: aisle length 1 + 44 + 1 = 46 LU.
HW = Layout(
    n_aisles=10,
    n_positions=45,
    location_length=1.0,
    aisle_spacing=5.0,
    end_offset=1.0,
    depot_offset=0.5,
)


def loc(aisle: int, position: int) -> Location:
    return Location(aisle, position)


def test_aisle_length():
    assert HW.aisle_length == 46


def test_same_aisle_is_straight_line():
    assert distance(loc(3, 5), loc(3, 20), HW) == 15
    assert distance(loc(3, 5), Location(3, 5, side=1), HW) == 0


def test_adjacent_aisles_near_front_go_via_front():
    # 5 across + 1 down + 1 up
    assert distance(loc(0, 0), loc(1, 0), HW) == 7


def test_adjacent_aisles_near_back_go_via_back():
    assert distance(loc(0, 44), loc(1, 44), HW) == 7


def test_cross_aisle_choice_takes_the_shorter_way():
    # y = 11 and 31: front 11 + 31 = 42, back 35 + 15 = 50
    assert distance(loc(0, 10), loc(1, 30), HW) == 5 + 42
    # y = 21 and 41: front 62, back 25 + 5 = 30
    assert distance(loc(2, 20), loc(7, 40), HW) == 25 + 30


def test_depot_to_first_location_matches_paper():
    # "The depot is 1.5 LU away from the first storage location of the leftmost aisle."
    assert distance(DEPOT, loc(0, 0), HW) == 1.5


def test_depot_to_far_corner():
    # 0.5 to the cross aisle, 45 across, 45 up
    assert distance(DEPOT, loc(9, 44), HW) == 90.5
    assert distance(DEPOT, DEPOT, HW) == 0


def test_distance_is_symmetric_and_satisfies_triangle_inequality():
    rng = random.Random(0)
    points = [DEPOT, *(loc(rng.randrange(10), rng.randrange(45)) for _ in range(30))]
    for a, b in itertools.combinations(points, 2):
        assert distance(a, b, HW) == distance(b, a, HW)
    for a, b, c in itertools.combinations(points, 3):
        assert distance(a, c, HW) <= distance(a, b, HW) + distance(b, c, HW) + 1e-9


def test_batch_size_and_locations():
    o1 = Order(0, (loc(0, 1), loc(2, 3)))
    o2 = Order(1, (loc(2, 3),), due_date=100.0)
    batch = Batch((o1, o2))
    assert batch.size == 3
    assert batch.locations == {loc(0, 1), loc(2, 3)}


def test_instance_rejects_locations_outside_the_layout():
    with pytest.raises(ValueError, match="outside the layout"):
        Instance("bad", HW, (Order(0, (loc(10, 0),)),), capacity=45)


def test_instance_rejects_orders_over_capacity():
    order = Order(0, tuple(loc(0, p) for p in range(5)))
    with pytest.raises(ValueError, match="exceeds capacity"):
        Instance("bad", HW, (order,), capacity=4)
