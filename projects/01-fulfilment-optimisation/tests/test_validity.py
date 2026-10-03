import pytest
from fulfilment_optimisation.domain import Location
from fulfilment_optimisation.validity import _lines_mix, aisles_visited, tvd, verdict

SETTINGS = {"tvd_match": 0.05, "tvd_close": 0.15}


def test_tvd():
    assert tvd([1, 1, 2, 2], [1, 1, 2, 2]) == 0
    assert tvd([1, 1], [2, 2]) == 1
    # P = {1: 0.5, 2: 0.5}, Q = {1: 0.75, 2: 0.25}: half of (0.25 + 0.25).
    assert tvd([1, 2], [1, 1, 1, 2]) == pytest.approx(0.25)


@pytest.mark.parametrize(
    ("distance", "expected"), [(0.0, "match"), (0.05, "match"), (0.1, "close"), (0.2, "mismatch")]
)
def test_verdict(distance, expected):
    assert verdict(distance, SETTINGS) == expected


def test_aisles_visited_counts_distinct_aisles():
    orders = [(Location(0, 1), Location(0, 5, 1)), (Location(0, 1), Location(3, 2), Location(7, 0))]
    assert aisles_visited(orders) == [1, 3]


def test_lines_mix():
    assert _lines_mix('{"value": 1}') == ([1], None)
    assert _lines_mix('{"population": [1, 2], "weights": [0.8, 0.2]}') == ([1, 2], [0.8, 0.2])
