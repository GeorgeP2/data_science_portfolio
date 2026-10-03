"""Checks that a solution is a valid batching of its instance."""

from __future__ import annotations

from collections import Counter

from fulfilment_optimisation.domain import Instance
from fulfilment_optimisation.solvers.base import Solution


def violations(instance: Instance, solution: Solution) -> list[str]:
    """Every way ``solution`` breaks the rules for ``instance``. Empty means feasible."""
    problems: list[str] = []
    expected = {order.id for order in instance.orders}
    seen = Counter(order.id for batch in solution.batches for order in batch.orders)

    for order_id in sorted(expected - seen.keys()):
        problems.append(f"order {order_id} is in no batch")
    for order_id in sorted(seen.keys() - expected):
        problems.append(f"order {order_id} is not in the instance")
    for order_id, count in sorted(seen.items()):
        if count > 1:
            problems.append(f"order {order_id} is in {count} batches")

    for i, batch in enumerate(solution.batches):
        if not batch.orders:
            problems.append(f"batch {i} is empty")
        if batch.size > instance.capacity:
            problems.append(f"batch {i} holds {batch.size} items, capacity is {instance.capacity}")

    if len(solution.routes) != len(solution.batches):
        problems.append(f"{len(solution.routes)} routes for {len(solution.batches)} batches")
    for i, (batch, route) in enumerate(zip(solution.batches, solution.routes, strict=False)):
        if set(route.stops) != batch.locations:
            problems.append(f"route {i} doesn't visit exactly the picks of batch {i}")

    total = sum(route.length for route in solution.routes)
    if abs(total - solution.total_distance) > 1e-6:
        problems.append(f"total distance {solution.total_distance} != sum of routes {total}")
    return problems


def check_feasible(instance: Instance, solution: Solution) -> None:
    """Raise ``ValueError`` listing every violation, if there are any."""
    if problems := violations(instance, solution):
        raise ValueError(f"{instance.name}: infeasible solution\n" + "\n".join(problems))
