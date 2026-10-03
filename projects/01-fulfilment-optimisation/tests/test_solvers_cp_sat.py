import random
import threading
import time
from pathlib import Path

import pytest

pytest.importorskip("ortools")

from fulfilment_optimisation.domain import Batch, Instance, Location, Order
from fulfilment_optimisation.parsers.henn_waescher import load_henn_waescher
from fulfilment_optimisation.routing import LargestGap, SShape
from fulfilment_optimisation.solvers import ALNS, Deadline, Incumbent, Savings, check_feasible
from fulfilment_optimisation.solvers.cp_sat import CPSATBatching

from portfolio import ProjectPaths, load_config

PATHS = ProjectPaths.from_file(__file__)
FIXTURE = Path(__file__).parent / "fixtures" / "henn_waescher" / "MTCR_X" / "1l-3-45-0.txt"
LAYOUT = load_henn_waescher(FIXTURE).layout


def random_instance(n_orders: int, capacity: int, seed: int) -> Instance:
    rng = random.Random(seed)
    orders = []
    for i in range(n_orders):
        picks = {
            Location(rng.randrange(LAYOUT.n_aisles), rng.randrange(LAYOUT.n_positions))
            for _ in range(rng.randint(1, 4))
        }
        orders.append(Order(i, tuple(sorted(picks))))
    return Instance(f"random-{n_orders}-{seed}", LAYOUT, tuple(orders), capacity)


def partitions(items: list[int]):
    """Every way to split ``items`` into non-empty groups."""
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for partition in partitions(rest):
        yield [[first], *partition]
        for k in range(len(partition)):
            yield [*partition[:k], [first, *partition[k]], *partition[k + 1 :]]


def brute_force(instance: Instance, router) -> float:
    best = float("inf")
    for partition in partitions(list(range(len(instance.orders)))):
        batches = [Batch(tuple(instance.orders[i] for i in group)) for group in partition]
        if all(b.size <= instance.capacity for b in batches):
            best = min(best, sum(router.length(b.locations, instance.layout) for b in batches))
    return best


@pytest.mark.parametrize("router", [SShape(), LargestGap()], ids=lambda r: r.name)
@pytest.mark.parametrize("seed", range(4))
def test_matches_brute_force(router, seed):
    instance = random_instance(7, capacity=6, seed=seed)
    solution = CPSATBatching(workers=1).solve(instance, router, Deadline.never())
    check_feasible(instance, solution)
    assert solution.finished
    assert solution.total_distance == pytest.approx(brute_force(instance, router), abs=1e-6)


def test_never_worse_than_warm_start_on_a_large_instance():
    instance = random_instance(60, capacity=12, seed=5)
    router = SShape()
    solution = CPSATBatching(pool_iterations=300).solve(instance, router, Deadline.never())
    check_feasible(instance, solution)
    warm = ALNS(seed=0, max_iterations=300).solve(instance, router, Deadline.never())
    assert solution.total_distance <= warm.total_distance + 1e-9
    assert (
        solution.total_distance
        <= Savings().solve(instance, router, Deadline.never()).total_distance
    )


def test_stops_within_50ms_of_deadline_and_returns_incumbent():
    instance = random_instance(80, capacity=12, seed=6)
    incumbent = Incumbent()
    begin = time.monotonic()
    solution = CPSATBatching(pool_iterations=10**9).solve(
        instance, SShape(), Deadline.after(0.5), incumbent
    )
    elapsed = time.monotonic() - begin
    assert elapsed < 0.55
    check_feasible(instance, solution)
    assert incumbent.best is not None
    assert incumbent.best.total_distance <= solution.total_distance + 1e-9


def test_incumbent_is_readable_while_running():
    instance = random_instance(80, capacity=12, seed=7)
    incumbent = Incumbent()
    thread = threading.Thread(
        target=CPSATBatching(pool_iterations=10**9).solve,
        args=(instance, SShape(), Deadline.after(1.0), incumbent),
    )
    thread.start()
    # Poll rather than sleep a fixed time: how soon the first solution lands depends on the machine.
    while incumbent.best is None and thread.is_alive():
        time.sleep(0.005)
    mid_run = incumbent.best
    still_running = thread.is_alive()
    thread.join()
    assert mid_run is not None
    assert still_running
    check_feasible(instance, mid_run)


def test_expired_deadline_returns_a_feasible_solution():
    instance = random_instance(30, capacity=12, seed=8)
    solution = CPSATBatching().solve(instance, SShape(), Deadline.after(0))
    check_feasible(instance, solution)
    assert not solution.finished


def test_config_parameters_are_accepted():
    CPSATBatching(seed=0, **load_config(PATHS.config).solvers["cp_sat"])
