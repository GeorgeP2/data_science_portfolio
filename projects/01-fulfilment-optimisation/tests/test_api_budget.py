import copy
import random
import time

import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from fulfilment_optimisation.api.app import create_app
from fulfilment_optimisation.api.schemas import _EXAMPLE_REQUEST
from fulfilment_optimisation.domain import Batch
from fulfilment_optimisation.registry import SOLVERS
from fulfilment_optimisation.solvers import Deadline, Incumbent, Savings, build_solution

from portfolio import ProjectPaths, load_config

CFG = load_config(ProjectPaths.from_file(__file__).config)
MARGIN_MS = CFG.api.response_margin_ms


class Sleeper:
    """Ignores the deadline. Optionally publishes the savings solution after ``publish_after``."""

    def __init__(self, sleep: float, publish_after: float | None = None) -> None:
        self.name = "sleeper"
        self.sleep, self.publish_after = sleep, publish_after

    def solve(self, instance, router, deadline: Deadline, incumbent: Incumbent | None = None):
        start = time.monotonic()
        if self.publish_after is not None:
            time.sleep(self.publish_after)
            if incumbent is not None:
                incumbent.offer(Savings().solve(instance, router, Deadline.never()))
        time.sleep(max(0.0, self.sleep - (time.monotonic() - start)))
        return Savings().solve(instance, router, Deadline.never())


class Crasher:
    name = "crasher"

    def solve(self, instance, router, deadline, incumbent=None):
        raise RuntimeError("boom")


class OnePerBatch:
    """Finishes at once with a solution worse than FCFS."""

    name = "one_per_batch"

    def solve(self, instance, router, deadline, incumbent=None):
        batches = [Batch((o,)) for o in instance.orders]
        return build_solution(batches, router, instance.layout, 0.0, finished=True)


TEST_SOLVERS = {
    **SOLVERS,
    "never_publishes": lambda seed, params: Sleeper(sleep=2.0),
    "publishes_early": lambda seed, params: Sleeper(sleep=2.0, publish_after=0.05),
    "crasher": lambda seed, params: Crasher(),
    "one_per_batch": lambda seed, params: OnePerBatch(),
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    from fulfilment_optimisation.api import schemas

    # The request model validates solver names against the registry; allow the test solvers.
    original = dict(schemas.SOLVERS)
    schemas.SOLVERS.update(TEST_SOLVERS)
    # As a context manager so the app's lifespan (garbage-collection settings) runs.
    with TestClient(create_app(CFG, solvers=TEST_SOLVERS)) as client:
        yield client
    schemas.SOLVERS.clear()
    schemas.SOLVERS.update(original)


def random_request(n_orders: int, seed: int, **changes) -> dict:
    rng = random.Random(seed)
    orders = [
        {
            "id": i,
            "locations": [
                {"aisle": rng.randrange(10), "position": rng.randrange(45)}
                for _ in range(rng.randint(1, 5))
            ],
        }
        for i in range(n_orders)
    ]
    body = copy.deepcopy(_EXAMPLE_REQUEST)
    body.update(orders=orders, capacity=15, **changes)
    return body


def post(client, body) -> tuple[dict, float]:
    """The response body and the server-side time from the ``Server-Timing`` header, in ms."""
    response = client.post("/batch", json=body)
    assert response.status_code == 200, response.text
    server_ms = float(response.headers["Server-Timing"].split("dur=")[1])
    return response.json(), server_ms


def fcfs_distance(client, body) -> float:
    return post(client, {**body, "solver": "fcfs"})[0]["total_distance"]


def test_tiny_budget_returns_fcfs_fallback(client):
    body = random_request(40, seed=1, solver="alns", budget_ms=1)
    result, _ = post(client, body)
    assert result["fallback_used"]
    assert result["solver"] == "fcfs"
    assert result["status"] == "deadline"
    assert result["total_distance"] == fcfs_distance(client, body)


def test_slow_solver_without_incumbent_falls_back_on_time(client):
    body = random_request(30, seed=2, solver="never_publishes", budget_ms=200)
    result, server_ms = post(client, body)
    assert server_ms < 200 + MARGIN_MS
    assert result["fallback_used"]
    assert result["solver"] == "fcfs"
    assert result["status"] == "deadline"


def test_slow_solver_returns_its_incumbent_on_time(client):
    body = random_request(30, seed=3, solver="publishes_early", budget_ms=300)
    result, server_ms = post(client, body)
    assert server_ms < 300 + MARGIN_MS
    assert not result["fallback_used"]
    assert result["solver"] == "sleeper"
    assert result["status"] == "deadline"
    assert result["total_distance"] <= fcfs_distance(client, body)


def test_crashing_solver_falls_back(client):
    result, _ = post(client, random_request(20, seed=4, solver="crasher"))
    assert result["fallback_used"]
    assert result["solver"] == "fcfs"


def test_result_worse_than_fcfs_is_replaced(client):
    body = random_request(20, seed=5, solver="one_per_batch")
    result, _ = post(client, body)
    assert result["fallback_used"]
    assert result["status"] == "finished"
    assert result["total_distance"] == fcfs_distance(client, body)


@pytest.mark.parametrize("solver", ["fcfs", "seed", "savings", "alns", "cp_sat"])
def test_generous_budget_is_never_worse_than_fcfs(client, solver):
    if solver == "cp_sat":
        pytest.importorskip("ortools")
    for seed in range(3):
        body = random_request(25, seed=10 + seed, solver=solver, budget_ms=300)
        result, _ = post(client, body)
        assert result["total_distance"] <= fcfs_distance(client, body) + 1e-9


def test_response_time_within_budget_for_99_percent(client):
    budget_ms = 50
    times = []
    for seed in range(100):
        n = random.Random(seed).choice([10, 50, 150, 300])
        _, server_ms = post(
            client, random_request(n, seed=seed, solver="alns", budget_ms=budget_ms)
        )
        times.append(server_ms)
    times.sort()
    p99 = times[98]
    # Server-side time: from the request arriving (before body parsing) to the response being ready.
    assert p99 <= budget_ms + MARGIN_MS, f"p99 {p99:.1f} ms; slowest {times[-3:]}"


def test_garbage_collection_runs_between_requests_not_during(client):
    import gc

    assert not gc.isenabled()  # the app's lifespan turned automatic collection off
    collections = gc.get_stats()[2]["collections"]
    post(client, random_request(20, seed=99, solver="fcfs"))
    assert gc.get_stats()[2]["collections"] > collections  # collected after the response
