import dataclasses
import time

import pytest
from fulfilment_optimisation.domain import Batch, Instance, Layout, Location, Order
from fulfilment_optimisation.parsers.henn_waescher import load_all
from fulfilment_optimisation.routing import LargestGap, SShape
from fulfilment_optimisation.solvers import (
    FCFS,
    Deadline,
    Incumbent,
    build_solution,
    check_feasible,
    violations,
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


def order(order_id: int, size: int) -> Order:
    return Order(order_id, tuple(Location(order_id % HW.n_aisles, p) for p in range(size)))


def instance(*sizes: int, capacity: int = 5) -> Instance:
    orders = tuple(order(i, size) for i, size in enumerate(sizes))
    return Instance("toy", HW, orders, capacity)


def batch_ids(solution) -> list[list[int]]:
    return [[o.id for o in batch.orders] for batch in solution.batches]


def test_fills_in_arrival_order():
    inst = instance(2, 3, 1, 4, 5, 1)
    solution = FCFS().solve(inst, ROUTER, Deadline.never())
    # 2 + 3 and 1 + 4 fill exactly, then 5 is full on its own and 1 starts the last batch.
    assert batch_ids(solution) == [[0, 1], [2, 3], [4], [5]]
    assert solution.finished
    check_feasible(inst, solution)
    assert solution.total_distance == sum(ROUTER.length(b.locations, HW) for b in solution.batches)


def test_does_not_skip_ahead_to_fill_a_batch():
    # Order 2 would fit in batch 0, but FCFS never looks past the order that overflowed.
    solution = FCFS().solve(instance(4, 3, 1), ROUTER, Deadline.never())
    assert batch_ids(solution) == [[0], [1, 2]]


def test_empty_instance():
    solution = FCFS().solve(instance(), ROUTER, Deadline.never())
    assert solution.batches == ()
    assert solution.total_distance == 0


def test_deterministic():
    inst = instance(2, 1, 4, 3, 2, 2, 5, 1)
    first = FCFS().solve(inst, ROUTER, Deadline.never())
    second = FCFS().solve(inst, ROUTER, Deadline.after(0))
    assert first.batches == second.batches
    assert first.routes == second.routes


def test_offers_solution_to_incumbent():
    incumbent = Incumbent()
    solution = FCFS().solve(instance(2, 3), ROUTER, Deadline.never(), incumbent)
    assert incumbent.best is solution


def test_incumbent_keeps_the_shorter_solution():
    inst = instance(1, 1)
    together = build_solution([Batch(inst.orders)], ROUTER, HW, 0.0, finished=True)
    apart = build_solution([Batch((o,)) for o in inst.orders], ROUTER, HW, 0.0, finished=True)
    shorter, longer = sorted([together, apart], key=lambda s: s.total_distance)
    assert shorter.total_distance < longer.total_distance

    incumbent = Incumbent()
    assert incumbent.best is None
    assert incumbent.offer(longer)
    assert incumbent.offer(shorter)
    assert not incumbent.offer(longer)
    assert incumbent.best is shorter


def test_deadline():
    assert not Deadline.never().expired()
    assert Deadline.never().remaining() == float("inf")
    assert Deadline.after(0).expired()
    assert Deadline.after(-1).remaining() == 0
    soon = Deadline.after(0.05)
    assert not soon.expired()
    assert 0 < soon.remaining() <= 0.05
    time.sleep(0.06)
    assert soon.expired()


def test_feasibility_catches_violations():
    inst = instance(2, 3, 4)
    good = FCFS().solve(inst, ROUTER, Deadline.never())
    assert violations(inst, good) == []

    o0, o1, o2 = inst.orders
    duplicated = build_solution([Batch((o0, o1)), Batch((o2, o0))], ROUTER, HW, 0.0, True)
    missing = build_solution([Batch((o0, o1))], ROUTER, HW, 0.0, True)
    overfull = build_solution([Batch((o0, o1, o2))], ROUTER, HW, 0.0, True)
    wrong_total = dataclasses.replace(good, total_distance=good.total_distance + 1)
    wrong_route = dataclasses.replace(good, routes=good.routes[::-1])

    assert violations(inst, duplicated) == [
        "order 0 is in 2 batches",
        "batch 1 holds 6 items, capacity is 5",
    ]
    assert violations(inst, missing) == ["order 2 is in no batch"]
    assert violations(inst, overfull) == ["batch 0 holds 9 items, capacity is 5"]
    assert violations(inst, wrong_total) == [
        f"total distance {wrong_total.total_distance} != sum of routes {good.total_distance}"
    ]
    assert len(violations(inst, wrong_route)) == 2
    with pytest.raises(ValueError, match="order 2 is in no batch"):
        check_feasible(inst, missing)


@pytest.mark.skipif(not RAW.is_dir(), reason="raw Henn & Wäscher data not downloaded")
@pytest.mark.parametrize("router", [SShape(), LargestGap()], ids=lambda r: r.name)
def test_feasible_on_all_henn_waescher_instances(router):
    for inst in load_all(RAW):
        solution = FCFS().solve(inst, router, Deadline.never())
        check_feasible(inst, solution)
        assert FCFS().solve(inst, router, Deadline.never()).batches == solution.batches
