"""Clarke & Wright savings batching, with savings recomputed after every merge.

Starts with one batch per order. The saving of merging batches ``A`` and ``B`` is
``d(A) + d(B) - d(A + B)``, where ``d`` is the router's tour length. The pair with the largest
saving whose combined size fits capacity is merged, and savings between the new batch and every
other batch are then **recomputed exactly** with the router (not approximated from order-level
savings). Merging stops when no pair fits or no saving is non-negative.

This is the C&W(ii) variant of de Koster, van der Poort & Wolters (1999). C&W(i), which ranks
order pairs once and never revisits the list, is not implemented.

Ties go to the pair of batches that formed earliest, so the result depends only on the instance.
The solver checks the deadline while costing pairs and between merges. If it runs out, it returns
the batches merged so far: they are always feasible, just less consolidated.

de Koster, M. B. M., van der Poort, E. S., Wolters, M. (1999). Efficient orderbatching methods in
warehouses. *International Journal of Production Research* 37(7), 1479-1504.
"""

from __future__ import annotations

import heapq
import itertools
import time
from dataclasses import dataclass

from fulfilment_optimisation.domain import Batch, Instance, Location, Order
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers.base import Deadline, Incumbent, Solution, build_solution


@dataclass(frozen=True, slots=True)
class _Group:
    orders: tuple[tuple[int, Order], ...]  # (arrival index, order), in arrival order
    size: int
    locations: frozenset[Location]
    cost: float


class Savings:
    name = "savings"

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        start = time.perf_counter()
        layout = instance.layout

        def group(orders: tuple[tuple[int, Order], ...]) -> _Group:
            locations = frozenset(loc for _, o in orders for loc in o.locations)
            size = sum(o.size for _, o in orders)
            return _Group(orders, size, locations, router.length(locations, layout))

        def merged(a: _Group, b: _Group) -> _Group:
            return group(tuple(sorted(a.orders + b.orders, key=lambda pair: pair[0])))

        groups = {i: group(((i, o),)) for i, o in enumerate(instance.orders)}
        next_id = itertools.count(len(groups))
        # Max-heap of (-saving, id_a, id_b, merged group); stale entries are skipped on pop.
        heap: list[tuple[float, int, int, _Group]] = []

        def push(a: int, b: int) -> None:
            ga, gb = groups[a], groups[b]
            if ga.size + gb.size > instance.capacity:
                return
            m = merged(ga, gb)
            saving = ga.cost + gb.cost - m.cost
            if saving >= 0:
                heapq.heappush(heap, (-saving, min(a, b), max(a, b), m))

        # Costing every pair is O(n^2) router calls (seconds at 500 orders), so it checks the
        # deadline too. If it runs out, no merges happen and the singletons are returned.
        finished = True
        for k, (a, b) in enumerate(itertools.combinations(groups, 2)):
            if k % 64 == 0 and deadline.expired():
                finished = False
                heap.clear()
                break
            push(a, b)

        while heap:
            if deadline.expired():
                finished = False
                break
            _, a, b, m = heapq.heappop(heap)
            if a not in groups or b not in groups:
                continue
            del groups[a], groups[b]
            new = next(next_id)
            groups[new] = m
            for other in list(groups):
                if other != new:
                    push(other, new)

        # Batches in the order their first order arrived.
        ordered = sorted(groups.values(), key=lambda g: g.orders[0][0])
        batches = [Batch(tuple(o for _, o in g.orders)) for g in ordered]
        solution = build_solution(
            batches, router, layout, time.perf_counter() - start, finished=finished
        )
        if incumbent is not None:
            incumbent.offer(solution)
        return solution
