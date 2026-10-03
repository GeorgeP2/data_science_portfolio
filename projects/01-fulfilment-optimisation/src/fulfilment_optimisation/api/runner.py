"""Run a solver under a hard latency budget, falling back to FCFS.

1. FCFS runs first. It takes microseconds and is the answer of last resort.
2. The requested solver runs in a worker thread with a deadline of ``budget - margin``. The margin
   covers FCFS, building the response and serialising it.
3. The handler waits for the worker only until that deadline, then takes the best of:
   - the solver's result, if it returned in time;
   - otherwise its incumbent (best solution so far), if it published one;
   - otherwise FCFS.
   The solver's answer is also replaced by FCFS if it's worse, so a response is never worse
   than FCFS. Either replacement sets ``fallback_used``, as does a solver raising an error
   (logged).

A worker that misses the deadline keeps running until it next checks the deadline (every solver
checks it between iterations). It's abandoned, not killed: threads can't be killed, and a process
per request would cost more than most budgets. The pool is bounded, so if every worker is busy,
the request waits for its deadline and falls back to FCFS rather than queueing indefinitely.
"""

from __future__ import annotations

import time
from concurrent.futures import Executor
from concurrent.futures import TimeoutError as FutureTimeout
from dataclasses import dataclass

from fulfilment_optimisation.domain import Instance
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers import FCFS, Deadline, Incumbent, Solution, Solver
from portfolio import get_logger

log = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class BudgetedResult:
    solution: Solution
    solver: str  # whose solution this is: the requested solver, or "fcfs" on fallback
    fallback_used: bool
    timed_out: bool  # the solver hadn't returned by the deadline


def run_with_budget(
    instance: Instance,
    solver: Solver,
    router: Router,
    budget_s: float,
    margin_s: float,
    executor: Executor,
    started_at: float | None = None,
) -> BudgetedResult:
    """``started_at`` (``time.monotonic()``) is when the request arrived; the budget runs from
    then, so time spent receiving and validating the request counts against it."""
    start = time.monotonic() if started_at is None else started_at
    deadline = Deadline(start + budget_s - margin_s)
    fcfs = FCFS().solve(instance, router, Deadline.never())

    def fallback(timed_out: bool) -> BudgetedResult:
        return BudgetedResult(fcfs, "fcfs", fallback_used=True, timed_out=timed_out)

    if deadline.expired():
        return fallback(timed_out=True)

    incumbent = Incumbent()
    future = executor.submit(solver.solve, instance, router, deadline, incumbent)
    try:
        solution = future.result(timeout=deadline.remaining())
        timed_out = False
    except FutureTimeout:
        future.cancel()  # only stops it if it never started
        best = incumbent.best
        if best is None:
            return fallback(timed_out=True)
        solution, timed_out = best, True
    except Exception:
        # A solver bug shouldn't fail the request when a valid FCFS answer is in hand.
        log.exception(
            "solver %s failed on %d orders; falling back to FCFS", solver.name, len(instance.orders)
        )
        return fallback(timed_out=False)

    if solution.total_distance > fcfs.total_distance + 1e-9:
        return fallback(timed_out)
    return BudgetedResult(solution, solver.name, fallback_used=False, timed_out=timed_out)
