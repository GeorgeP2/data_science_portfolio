import time
from pathlib import Path

import pytest
from fulfilment_optimisation.benchmark import grid, run_grid, summarise
from fulfilment_optimisation.domain import Batch, Instance, Location, Order
from fulfilment_optimisation.parsers.henn_waescher import load_henn_waescher
from fulfilment_optimisation.registry import SOLVERS
from fulfilment_optimisation.solvers import Deadline, Incumbent, Solution, build_solution

FIXTURE = Path(__file__).parent / "fixtures" / "henn_waescher" / "MTCR_X" / "1l-3-45-0.txt"


class OnePerBatch:
    """Every order on its own: a second solver for the grid that is easy to reason about."""

    name = "one_per_batch"

    def solve(
        self,
        instance: Instance,
        router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        start = time.perf_counter()
        batches = [Batch((order,)) for order in instance.orders]
        return build_solution(batches, router, instance.layout, time.perf_counter() - start, True)


SMOKE_SOLVERS = {**SOLVERS, "one_per_batch": lambda seed: OnePerBatch()}


@pytest.fixture(scope="module")
def instances() -> list[Instance]:
    hw = load_henn_waescher(FIXTURE)
    # Two small orders in one aisle, so FCFS batches them together.
    toy = Instance(
        "toy",
        hw.layout,
        (Order(0, (Location(2, 5),)), Order(1, (Location(2, 30),))),
        capacity=hw.capacity,
    )
    return [hw, toy]


def smoke_grid(instances):
    return grid(instances, ["fcfs", "one_per_batch"], ["s_shape", "largest_gap"], [0.5], [0, 1])


def test_smoke_grid(instances):
    results = run_grid(smoke_grid(instances), solvers=SMOKE_SOLVERS)
    assert len(results) == 2 * 2 * 2 * 1 * 2
    assert results.finished.all()
    assert (results.distance > 0).all()

    summary = summarise(results)
    assert len(summary) == 2 * 2
    fcfs = summary[summary.solver == "fcfs"]
    assert (fcfs.mean_saved_vs_fcfs_pct == 0).all()
    # Splitting orders can only add walking, never save it.
    assert (summary[summary.solver == "one_per_batch"].mean_saved_vs_fcfs_pct < 0).all()
    assert (summary.solve_time_p95_ms >= summary.solve_time_p50_ms).all()


def test_rerun_gives_identical_distances(instances):
    runs = smoke_grid(instances)
    first = run_grid(runs, solvers=SMOKE_SOLVERS)
    second = run_grid(runs, solvers=SMOKE_SOLVERS)
    cols = ["instance", "solver", "router", "seed", "distance", "n_batches"]
    assert first[cols].equals(second[cols])


def test_process_pool_matches_in_process(instances):
    runs = grid(instances, ["fcfs"], ["s_shape", "largest_gap"], [0.5], [0])
    pooled = run_grid(runs, workers=2)
    local = run_grid(runs)
    assert pooled.distance.tolist() == local.distance.tolist()


def test_summary_without_fcfs_leaves_savings_blank(instances):
    runs = grid(instances, ["one_per_batch"], ["s_shape"], [0.5], [0])
    summary = summarise(run_grid(runs, solvers=SMOKE_SOLVERS))
    assert summary.mean_saved_vs_fcfs_pct.isna().all()
