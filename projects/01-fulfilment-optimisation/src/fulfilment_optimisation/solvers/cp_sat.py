"""Order batching as set partitioning over a pool of candidate batches, solved with CP-SAT.

**Formulation.** Tour length isn't linear in batch membership, so the model doesn't try to express
routing. It picks from a pool ``P`` of candidate batches, each feasible (within capacity) and costed
*exactly* by the router::

    minimise    sum_{b in P} cost(b) * x_b
    subject to  sum_{b in P : o in b} x_b = 1   for every order o
                x_b in {0, 1}

Costs are scaled by ``cost_scale`` and rounded to integers, as CP-SAT requires.

**The approximation is the pool, not the distance.** Every solution is costed exactly, but the
optimum is only optimal *over the pool*. Small instances (``n <= enumerate_up_to`` orders) get
every feasible subset, so the model is exact. Larger ones get every batch that ALNS generated as a
candidate during ``pool_fraction`` of the budget, plus all single-order batches, which keeps the
model feasible. CP-SAT can then recombine batches that ALNS never had in one solution.

**Warm start.** The best ALNS solution (or savings, when enumerating) is the solution hint, and
it's returned if CP-SAT doesn't beat it, so the result is never worse than the warm start.

**Anytime.** A solution callback offers every improving solution to the incumbent. CP-SAT's time
limit is set to the deadline minus ``deadline_margin``, with a timer as a backstop, because the
limit isn't hard when the CPU is contended. Even so, at long budgets (5-10 s, pools of ~16k
batches) CP-SAT occasionally keeps searching for up to ~1 s after both: 10 of 1,344 runs in the
Pareto sweep. Its search log showed nothing unusual, and the service is unaffected because the
runner returns the incumbent at the deadline. ``finished`` is True only when CP-SAT proves
optimality over the pool.
"""

from __future__ import annotations

import itertools
import threading
import time

from ortools.sat.python import cp_model

from fulfilment_optimisation.domain import Batch, Instance
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers.alns import ALNS
from fulfilment_optimisation.solvers.base import Deadline, Incumbent, Solution, build_solution
from fulfilment_optimisation.solvers.savings import Savings


class CPSATBatching:
    name = "cp_sat"

    def __init__(
        self,
        seed: int = 0,
        pool_fraction: float = 0.5,
        pool_iterations: int = 5_000,
        enumerate_up_to: int = 12,
        workers: int = 4,
        cost_scale: int = 1000,
        deadline_margin: float = 0.02,
    ) -> None:
        self.seed = seed
        self.pool_fraction = pool_fraction
        self.pool_iterations = pool_iterations
        self.enumerate_up_to = enumerate_up_to
        self.workers = workers
        self.cost_scale = cost_scale
        self.deadline_margin = deadline_margin

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        start = time.perf_counter()
        n = len(instance.orders)
        sizes = [o.size for o in instance.orders]
        index = {o.id: i for i, o in enumerate(instance.orders)}

        def to_solution(batches: list[frozenset[int]], finished: bool) -> Solution:
            ordered = sorted((sorted(b) for b in batches), key=lambda b: b[0])
            return build_solution(
                [Batch(tuple(instance.orders[i] for i in b)) for b in ordered],
                router,
                instance.layout,
                time.perf_counter() - start,
                finished,
            )

        # --- candidate pool and warm start ---
        pool: set[frozenset[int]] = {frozenset((i,)) for i in range(n)}
        if n <= self.enumerate_up_to:
            for k in range(2, n + 1):
                for combo in itertools.combinations(range(n), k):
                    if sum(sizes[i] for i in combo) <= instance.capacity:
                        pool.add(frozenset(combo))
            warm = Savings().solve(instance, router, deadline, incumbent)
        else:
            if deadline.expires_at == float("inf"):
                pool_deadline = deadline
            else:
                pool_deadline = Deadline.after(self.pool_fraction * deadline.remaining())
            alns = ALNS(seed=self.seed, max_iterations=self.pool_iterations)
            warm = alns.search(instance, router, pool_deadline, incumbent, visited=pool)
        warm_batches = [frozenset(index[o.id] for o in b.orders) for b in warm.batches]
        pool.update(warm_batches)
        if deadline.expired():
            return to_solution(warm_batches, finished=False)

        # --- model ---
        candidates = sorted(pool, key=lambda b: (len(b), sorted(b)))
        layout = instance.layout
        locations = [frozenset(o.locations) for o in instance.orders]

        def cost(batch: frozenset[int]) -> int:
            route_locations = frozenset().union(*(locations[i] for i in batch))
            return round(self.cost_scale * router.length(route_locations, layout))

        model = cp_model.CpModel()
        x = [model.NewBoolVar(f"x{k}") for k in range(len(candidates))]
        covering: list[list[cp_model.IntVar]] = [[] for _ in range(n)]
        for var, batch in zip(x, candidates, strict=True):
            for i in batch:
                covering[i].append(var)
        for vars_ in covering:
            model.AddExactlyOne(vars_)
        model.Minimize(sum(cost(b) * var for b, var in zip(candidates, x, strict=True)))
        hinted = set(warm_batches)
        for var, batch in zip(x, candidates, strict=True):
            model.AddHint(var, batch in hinted)

        remaining = deadline.remaining() - self.deadline_margin
        if remaining <= 0:
            return to_solution(warm_batches, finished=False)

        solver = cp_model.CpSolver()
        if remaining != float("inf"):
            solver.parameters.max_time_in_seconds = remaining
        solver.parameters.num_workers = self.workers
        solver.parameters.random_seed = self.seed

        def chosen(values) -> list[frozenset[int]]:
            return [b for b, var in zip(candidates, x, strict=True) if values(var)]

        class _Callback(cp_model.CpSolverSolutionCallback):
            def on_solution_callback(self) -> None:
                if incumbent is not None:
                    incumbent.offer(to_solution(chosen(self.BooleanValue), finished=False))

        # CP-SAT's time limit isn't hard under CPU contention, so a timer also stops the search
        # once the deadline (less half the margin, for building the result) arrives.
        timer = None
        if remaining != float("inf"):
            timer = threading.Timer(
                max(0.0, deadline.remaining() - self.deadline_margin / 2), solver.StopSearch
            )
            timer.start()
        try:
            status = solver.Solve(model, _Callback())
        finally:
            if timer is not None:
                timer.cancel()
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            return to_solution(warm_batches, finished=False)

        solution = to_solution(chosen(solver.BooleanValue), finished=status == cp_model.OPTIMAL)
        if solution.total_distance > warm.total_distance + 1e-9:
            solution = to_solution(warm_batches, finished=solution.finished)
        if incumbent is not None:
            incumbent.offer(solution)
        return solution
