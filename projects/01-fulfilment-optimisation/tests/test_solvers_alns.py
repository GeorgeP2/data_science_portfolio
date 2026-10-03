import random
import threading
import time
from pathlib import Path

import pytest
from fulfilment_optimisation.domain import Instance, Location, Order
from fulfilment_optimisation.parsers.henn_waescher import load_all, load_henn_waescher
from fulfilment_optimisation.routing import LargestGap, SShape
from fulfilment_optimisation.solvers import ALNS, Deadline, Incumbent, Savings, check_feasible

from portfolio import ProjectPaths, load_config

PATHS = ProjectPaths.from_file(__file__)
RAW = PATHS.raw / "henn_waescher" / "obsp_instances"
FIXTURE = Path(__file__).parent / "fixtures" / "henn_waescher" / "MTCR_X" / "1l-3-45-0.txt"
LAYOUT = load_henn_waescher(FIXTURE).layout


def random_instance(n_orders: int, capacity: int, seed: int) -> Instance:
    rng = random.Random(seed)
    orders = []
    for i in range(n_orders):
        picks = {
            Location(rng.randrange(LAYOUT.n_aisles), rng.randrange(LAYOUT.n_positions))
            for _ in range(rng.randint(1, 6))
        }
        orders.append(Order(i, tuple(sorted(picks))))
    return Instance(f"random-{seed}", LAYOUT, tuple(orders), capacity)


INSTANCES = [random_instance(30, 12, seed) for seed in range(3)]


@pytest.mark.parametrize("router", [SShape(), LargestGap()], ids=lambda r: r.name)
@pytest.mark.parametrize("instance", INSTANCES, ids=lambda i: i.name)
def test_feasible_and_never_worse_than_savings(instance, router):
    solution = ALNS(seed=1, max_iterations=300).solve(instance, router, Deadline.never())
    check_feasible(instance, solution)
    assert solution.finished
    start = Savings().solve(instance, router, Deadline.never())
    assert solution.total_distance <= start.total_distance + 1e-9


def test_improves_on_savings_given_iterations():
    router = SShape()
    alns = sum(
        ALNS(seed=0, max_iterations=500).solve(i, router, Deadline.never()).total_distance
        for i in INSTANCES
    )
    savings = sum(Savings().solve(i, router, Deadline.never()).total_distance for i in INSTANCES)
    assert alns < savings


def test_deterministic_for_fixed_seed_and_iterations():
    instance = INSTANCES[0]
    runs = [
        ALNS(seed=7, max_iterations=200).solve(instance, SShape(), Deadline.never())
        for _ in range(2)
    ]
    assert runs[0].batches == runs[1].batches
    assert runs[0].total_distance == runs[1].total_distance


def test_stops_within_50ms_of_deadline():
    instance = random_instance(80, 45, seed=11)
    solver = ALNS(seed=0, max_iterations=10**9)
    begin = time.monotonic()
    solution = solver.solve(instance, SShape(), Deadline.after(0.3))
    elapsed = time.monotonic() - begin
    assert not solution.finished
    assert 0.3 <= elapsed < 0.35
    check_feasible(instance, solution)


def test_incumbent_is_readable_while_running():
    instance = random_instance(80, 45, seed=12)
    incumbent = Incumbent()
    thread = threading.Thread(
        target=ALNS(seed=0, max_iterations=10**9).solve,
        args=(instance, SShape(), Deadline.after(0.5), incumbent),
    )
    thread.start()
    time.sleep(0.1)
    mid_run = incumbent.best
    thread.join()
    assert mid_run is not None
    check_feasible(instance, mid_run)
    assert incumbent.best is not None
    assert incumbent.best.total_distance <= mid_run.total_distance


def test_expired_deadline_returns_savings_start():
    instance = INSTANCES[1]
    solution = ALNS(seed=0).solve(instance, SShape(), Deadline.after(0))
    check_feasible(instance, solution)
    assert not solution.finished


def test_single_order():
    instance = random_instance(1, 12, seed=3)
    solution = ALNS().solve(instance, SShape(), Deadline.never())
    check_feasible(instance, solution)


def test_config_parameters_are_accepted():
    params = load_config(PATHS.config).solvers["alns"]
    ALNS(seed=0, **params)


@pytest.mark.skipif(not RAW.is_dir(), reason="raw Henn & Wäscher data not downloaded")
def test_feasible_on_henn_waescher_sample():
    # Every 12th instance with a short iteration cap keeps this quick; the 1 s comparison with
    # savings is in the benchmark (see the T13 PR).
    for instance in load_all(RAW)[::12]:
        solution = ALNS(seed=0, max_iterations=200).solve(instance, LargestGap(), Deadline.never())
        check_feasible(instance, solution)
