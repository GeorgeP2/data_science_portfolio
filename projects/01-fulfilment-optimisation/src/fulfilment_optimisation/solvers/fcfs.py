"""First-come-first-served batching: the baseline every other solver is compared with.

Orders are taken in arrival order (the order the instance lists them) and added to the current
batch until the next one would exceed picker capacity. That order then starts a new batch. Batches
are never revisited, so the result depends only on the instance.
"""

from __future__ import annotations

import time

from fulfilment_optimisation.domain import Batch, Instance, Order
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers.base import Deadline, Incumbent, Solution, build_solution


class FCFS:
    name = "fcfs"

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        # One pass with no search, so the deadline is ignored.
        start = time.perf_counter()
        batches: list[Batch] = []
        current: list[Order] = []
        load = 0
        for order in instance.orders:
            if current and load + order.size > instance.capacity:
                batches.append(Batch(tuple(current)))
                current, load = [], 0
            current.append(order)
            load += order.size
        if current:
            batches.append(Batch(tuple(current)))

        solution = build_solution(
            batches, router, instance.layout, time.perf_counter() - start, finished=True
        )
        if incumbent is not None:
            incumbent.offer(solution)
        return solution
