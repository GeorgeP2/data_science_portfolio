import pytest
from fulfilment_optimisation.domain import Instance, Layout, Location, Order
from fulfilment_optimisation.parsers.henn_waescher import load_all
from fulfilment_optimisation.routing import LargestGap, SShape
from fulfilment_optimisation.solvers import (
    FCFS,
    Deadline,
    Incumbent,
    Savings,
    SeedBatching,
    check_feasible,
)

from portfolio import ProjectPaths

RAW = ProjectPaths.from_file(__file__).raw / "henn_waescher" / "obsp_instances"
HW = Layout(
    n_aisles=10,
    n_positions=45,
    location_length=1.0,
    aisle_spacing=5.0,
    end_offset=1.0,
    depot_offset=0.5,
)
ROUTER = SShape()
HEURISTICS = [SeedBatching(), Savings()]


def order(order_id: int, *locations: tuple[int, int]) -> Order:
    return Order(order_id, tuple(Location(a, p) for a, p in locations))


# Arrivals alternate between the front of aisle 0 and the back of aisle 9, so FCFS pairs each
# near order with a far one and crosses the warehouse twice.
CROSSING = Instance(
    "crossing",
    HW,
    (order(0, (0, 2)), order(1, (9, 40)), order(2, (0, 5)), order(3, (9, 30))),
    capacity=2,
)


def batch_ids(solution) -> list[list[int]]:
    return [[o.id for o in batch.orders] for batch in solution.batches]


@pytest.mark.parametrize("solver", HEURISTICS, ids=lambda s: s.name)
def test_known_answer(solver):
    solution = solver.solve(CROSSING, ROUTER, Deadline.never())
    assert batch_ids(solution) == [[0, 2], [1, 3]]
    # Aisle 0 in and back to y = 6: 1 + 12. Aisle 9 in and back to y = 41: 1 + 90 + 82.
    assert solution.total_distance == 13 + 173
    assert FCFS().solve(CROSSING, ROUTER, Deadline.never()).total_distance == 2 * 183
    assert solution.finished


@pytest.mark.parametrize("solver", HEURISTICS, ids=lambda s: s.name)
def test_respects_capacity_and_is_deterministic(solver):
    orders = tuple(order(i, (i % 4, i), ((i * 3) % 10, 40 - i)) for i in range(12))
    instance = Instance("mixed", HW, orders, capacity=5)
    first = solver.solve(instance, ROUTER, Deadline.never())
    check_feasible(instance, first)
    assert all(batch.size <= 5 for batch in first.batches)
    assert solver.solve(instance, ROUTER, Deadline.never()).batches == first.batches


@pytest.mark.parametrize("solver", HEURISTICS, ids=lambda s: s.name)
def test_offers_to_incumbent(solver):
    incumbent = Incumbent()
    solution = solver.solve(CROSSING, ROUTER, Deadline.never(), incumbent)
    assert incumbent.best is solution


def test_seed_picks_the_widest_order_first():
    wide = order(5, (1, 0), (4, 0), (7, 0))
    instance = Instance("seed", HW, (order(0, (2, 3)), wide, order(9, (4, 10))), capacity=4)
    solution = SeedBatching().solve(instance, ROUTER, Deadline.never())
    # The 3-aisle order seeds the first batch; order 9 adds no new aisle, so it joins first.
    assert batch_ids(solution) == [[5, 9], [0]]


def test_seed_rejects_unknown_rules():
    with pytest.raises(ValueError, match="unknown seed rule"):
        SeedBatching(seed_rule="tallest")
    with pytest.raises(ValueError, match="unknown addition rule"):
        SeedBatching(addition_rule="nearest_star")


def test_savings_returns_feasible_partial_result_at_deadline():
    solution = Savings().solve(CROSSING, ROUTER, Deadline.after(0))
    check_feasible(CROSSING, solution)
    assert not solution.finished
    assert batch_ids(solution) == [[0], [1], [2], [3]]


@pytest.mark.skipif(not RAW.is_dir(), reason="raw Henn & Wäscher data not downloaded")
@pytest.mark.parametrize("router", [SShape(), LargestGap()], ids=lambda r: r.name)
def test_feasible_and_beat_fcfs_on_henn_waescher(router):
    instances = load_all(RAW)
    totals = {"fcfs": 0.0, "seed": 0.0, "savings": 0.0}
    for instance in instances:
        for solver in [FCFS(), *HEURISTICS]:
            solution = solver.solve(instance, router, Deadline.never())
            check_feasible(instance, solution)
            totals[solver.name] += solution.total_distance
    assert totals["seed"] < totals["fcfs"]
    assert totals["savings"] < totals["fcfs"]
