import random
import time
from pathlib import Path

import pytest

pytest.importorskip("ortools")

from fulfilment_optimisation.domain import Instance, Location, Order
from fulfilment_optimisation.parsers.henn_waescher import load_henn_waescher
from fulfilment_optimisation.registry import SOLVERS
from fulfilment_optimisation.routing import LargestGap, Optimal, SShape
from fulfilment_optimisation.solvers import Deadline, Incumbent, check_feasible
from fulfilment_optimisation.solvers.ortools_routing import ORToolsRouting, centre_of_gravity

from portfolio import ProjectPaths, load_config

PATHS = ProjectPaths.from_file(__file__)
FIXTURE = Path(__file__).parent / "fixtures" / "henn_waescher" / "MTCR_X" / "1l-3-45-0.txt"
LAYOUT = load_henn_waescher(FIXTURE).layout
MODELS = ["order_nodes", "pick_nodes"]


def random_instance(n_orders: int, capacity: int, seed: int, max_picks: int = 4) -> Instance:
    rng = random.Random(seed)
    orders = []
    for i in range(n_orders):
        picks = {
            Location(rng.randrange(LAYOUT.n_aisles), rng.randrange(LAYOUT.n_positions))
            for _ in range(rng.randint(1, max_picks))
        }
        orders.append(Order(i, tuple(sorted(picks))))
    return Instance(f"random-{n_orders}-{seed}", LAYOUT, tuple(orders), capacity)


@pytest.mark.parametrize("model", MODELS)
@pytest.mark.parametrize("router", [SShape(), LargestGap(), Optimal()], ids=lambda r: r.name)
@pytest.mark.parametrize("seed", range(3))
def test_batches_are_feasible_and_rescored_by_the_router(model, router, seed):
    instance = random_instance(25, capacity=10, seed=seed)
    solution = ORToolsRouting(model=model).solve(instance, router, Deadline.after(0.3))
    check_feasible(instance, solution)  # every order once, capacity, routes visit every pick
    for batch, route in zip(solution.batches, solution.routes, strict=True):
        assert route.length == pytest.approx(router.length(batch.locations, instance.layout))


@pytest.mark.parametrize("seed", range(5))
def test_pick_node_tours_match_optimal_routing_on_small_instances(seed):
    # Pick nodes make each vehicle a travelling-salesman tour over shortest walking distances,
    # which is what Ratliff & Rosenthal's DP solves exactly. OR-Tools should find those tours.
    instance = random_instance(6, capacity=8, seed=seed, max_picks=3)
    solver = ORToolsRouting(model="pick_nodes")
    solution = solver.solve(instance, Optimal(), Deadline.after(0.5))
    check_feasible(instance, solution)
    assert solver.model_cost == pytest.approx(solution.total_distance, abs=1e-6)


@pytest.mark.parametrize("seed", range(3))
def test_pick_node_tours_are_never_shorter_than_optimal(seed):
    instance = random_instance(40, capacity=12, seed=seed)
    solver = ORToolsRouting(model="pick_nodes")
    # No deadline: OR-Tools stops at its first local optimum. With one, a slow runner could spend
    # it all on the savings start and skip the search.
    solution = solver.solve(instance, Optimal(), Deadline.never())
    assert solver.model_cost is not None
    assert solver.model_cost >= solution.total_distance - 1e-6
    # Within 5% of the exact tours on these batches.
    assert solver.model_cost <= 1.05 * solution.total_distance


def test_centre_of_gravity_rounds_the_mean_aisle_and_position():
    order = Order(0, (Location(1, 10), Location(4, 20), Location(4, 31)))
    assert centre_of_gravity(order) == Location(3, 20)


def test_stops_within_50ms_of_deadline_and_offers_the_incumbent():
    # Five runs, judged on the median, so a one-off stall on a shared CI runner doesn't fail it.
    instance = random_instance(80, capacity=12, seed=6)
    elapsed = []
    for _ in range(5):
        incumbent = Incumbent()
        begin = time.monotonic()
        solution = ORToolsRouting().solve(instance, SShape(), Deadline.after(0.3), incumbent)
        elapsed.append(time.monotonic() - begin)
        check_feasible(instance, solution)
        assert not solution.finished
        assert incumbent.best is not None
        assert incumbent.best.total_distance <= solution.total_distance + 1e-9
    assert sorted(elapsed)[2] < 0.35, elapsed


def test_expired_deadline_returns_a_feasible_solution():
    instance = random_instance(30, capacity=12, seed=8)
    solver = ORToolsRouting()
    solution = solver.solve(instance, SShape(), Deadline.after(0))
    check_feasible(instance, solution)
    assert not solution.finished
    assert solver.model_cost is None


def test_without_a_deadline_it_stops_at_a_local_optimum():
    instance = random_instance(30, capacity=12, seed=9)
    solution = ORToolsRouting().solve(instance, SShape(), Deadline.never())
    check_feasible(instance, solution)
    assert solution.finished


def test_rejects_unknown_settings():
    with pytest.raises(ValueError, match="model"):
        ORToolsRouting(model="stops")
    with pytest.raises(ValueError, match="metaheuristic"):
        ORToolsRouting(metaheuristic="ANNEALING_PLEASE")


def test_registered_with_the_config_parameters():
    params = load_config(PATHS.config).solvers["ortools"]
    assert isinstance(SOLVERS["ortools"](0, params), ORToolsRouting)
