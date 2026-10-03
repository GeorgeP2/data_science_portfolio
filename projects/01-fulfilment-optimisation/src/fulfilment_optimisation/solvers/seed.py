"""Seed batching: open each batch with a seed order, then grow it with the most congruent orders.

Follows the seed algorithms surveyed by de Koster, van der Poort & Wolters (1999). Each batch is
built in two steps:

1. **Seed selection.** ``most_aisles``: the unassigned order that visits the most distinct aisles,
   so the hardest-to-combine orders anchor batches instead of being left over.
2. **Order addition**, repeated until no unassigned order fits. ``fewest_new_aisles``: the order
   that adds the fewest aisles not already visited by the batch (the "number of additional aisles"
   congruency rule). Congruency is measured against the whole batch so far (cumulative), not just
   the seed.

Ties go to the order that arrived first, so the result depends only on the instance.

de Koster, M. B. M., van der Poort, E. S., Wolters, M. (1999). Efficient orderbatching methods in
warehouses. *International Journal of Production Research* 37(7), 1479-1504.
"""

from __future__ import annotations

import time
from collections.abc import Callable

from fulfilment_optimisation.domain import Batch, Instance, Order
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers.base import Deadline, Incumbent, Solution, build_solution


def _aisles(order: Order) -> frozenset[int]:
    return frozenset(loc.aisle for loc in order.locations)


# Higher is a better seed.
SEED_RULES: dict[str, Callable[[Order], float]] = {
    "most_aisles": lambda order: len(_aisles(order)),
}
# Lower is a better addition, given the aisles the batch already visits.
ADDITION_RULES: dict[str, Callable[[Order, frozenset[int]], float]] = {
    "fewest_new_aisles": lambda order, aisles: len(_aisles(order) - aisles),
}


class SeedBatching:
    name = "seed"

    def __init__(
        self, seed_rule: str = "most_aisles", addition_rule: str = "fewest_new_aisles"
    ) -> None:
        if seed_rule not in SEED_RULES:
            raise ValueError(f"unknown seed rule {seed_rule!r}; choose from {sorted(SEED_RULES)}")
        if addition_rule not in ADDITION_RULES:
            raise ValueError(
                f"unknown addition rule {addition_rule!r}; choose from {sorted(ADDITION_RULES)}"
            )
        self.seed_score = SEED_RULES[seed_rule]
        self.addition_cost = ADDITION_RULES[addition_rule]

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        # Constructive, no search: the deadline is ignored.
        start = time.perf_counter()
        # Indices preserve arrival order for tie-breaks.
        unassigned = dict(enumerate(instance.orders))
        batches: list[Batch] = []
        while unassigned:
            seed_idx = max(unassigned, key=lambda i: (self.seed_score(unassigned[i]), -i))
            members = [unassigned.pop(seed_idx)]
            load = members[0].size
            aisles = _aisles(members[0])
            while True:
                fits = [i for i, o in unassigned.items() if load + o.size <= instance.capacity]
                if not fits:
                    break
                best = min(fits, key=lambda i: (self.addition_cost(unassigned[i], aisles), i))
                order = unassigned.pop(best)
                members.append(order)
                load += order.size
                aisles |= _aisles(order)
            batches.append(Batch(tuple(members)))

        solution = build_solution(
            batches, router, instance.layout, time.perf_counter() - start, finished=True
        )
        if incumbent is not None:
            incumbent.offer(solution)
        return solution
