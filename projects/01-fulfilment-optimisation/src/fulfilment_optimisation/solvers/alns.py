"""Adaptive large neighbourhood search (ALNS) for order batching.

Follows the ALNS framework of Ropke & Pisinger (2006), adapted from vehicle routing to batching.
Each iteration removes some orders from the current solution (destroy), puts them back (repair)
and accepts or rejects the result with simulated annealing.

- **Start:** the Clarke & Wright savings solution (``solvers.savings``).
- **Destroy:** ``random`` removes uniformly chosen orders. ``worst`` removes the orders whose
  removal shortens their batch's tour most. ``related`` removes a random order and the orders
  whose aisle sets overlap it most (Jaccard similarity), a batching version of Shaw removal.
  ``worst`` and ``related`` pick from their ranked lists with Ropke & Pisinger's randomisation:
  index ``floor(y ** determinism * len)`` for uniform ``y``.
- **Repair:** ``greedy`` repeatedly inserts the order whose cheapest insertion is cheapest.
  ``regret`` (regret-2) inserts the order with the largest gap between its best and second-best
  insertion. Opening a new batch is always an option, and both respect capacity.
- **Acceptance:** simulated annealing. The start temperature accepts a solution
  ``start_worse_accept`` worse than the start with probability 0.5; it cools geometrically each
  iteration.
- **Adaptive weights:** each segment of ``segment_length`` iterations, an operator's weight moves
  towards its average score, with ``reaction`` as the step. An operator scores ``scores[0]`` for a
  new best, ``scores[1]`` for improving the current solution and ``scores[2]`` for an accepted
  worse one.

Batch tour lengths are cached by the set of orders in the batch, since routing dominates run time.

The search stops at the deadline or after ``max_iterations``, whichever comes first, and returns
the best solution found. Every improvement on the best is offered to the incumbent. With a fixed
seed and ``max_iterations``, results are deterministic. Under a deadline, the iteration count (and
so the result) depends on machine speed.

Ropke, S., Pisinger, D. (2006). An adaptive large neighborhood search heuristic for the pickup
and delivery problem with time windows. *Transportation Science* 40(4), 455-472.
"""

from __future__ import annotations

import heapq
import math
import random
import time
from collections.abc import Callable, Sequence

from fulfilment_optimisation.domain import Batch, Instance, Location
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers.base import Deadline, Incumbent, Solution, build_solution
from fulfilment_optimisation.solvers.savings import Savings

Batches = list[frozenset[int]]  # each batch is a set of order indices (arrival positions)


class _Costs:
    """Tour length per batch, cached by the batch's order indices."""

    def __init__(self, instance: Instance, router: Router, max_size: int) -> None:
        self.locations: list[frozenset[Location]] = [
            frozenset(o.locations) for o in instance.orders
        ]
        self.router = router
        self.layout = instance.layout
        self.max_size = max_size
        self.cache: dict[frozenset[int], float] = {}

    def __call__(self, batch: frozenset[int]) -> float:
        cost = self.cache.get(batch)
        if cost is None:
            if len(self.cache) >= self.max_size:
                self.cache.clear()
            locations = frozenset().union(*(self.locations[i] for i in batch))
            cost = self.cache[batch] = self.router.length(locations, self.layout)
        return cost


class ALNS:
    name = "alns"

    def __init__(
        self,
        seed: int = 0,
        max_iterations: int = 20_000,
        remove_min: int = 2,
        remove_max_fraction: float = 0.3,
        determinism: float = 4.0,
        start_worse_accept: float = 0.05,
        cooling: float = 0.9995,
        segment_length: int = 100,
        reaction: float = 0.1,
        scores: Sequence[float] = (33.0, 9.0, 13.0),
        cache_size: int = 200_000,
    ) -> None:
        self.seed = seed
        self.max_iterations = max_iterations
        self.remove_min = remove_min
        self.remove_max_fraction = remove_max_fraction
        self.determinism = determinism
        self.start_worse_accept = start_worse_accept
        self.cooling = cooling
        self.segment_length = segment_length
        self.reaction = reaction
        self.scores = tuple(scores)
        self.cache_size = cache_size

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        start = time.perf_counter()
        rng = random.Random(self.seed)
        n = len(instance.orders)
        sizes = [o.size for o in instance.orders]
        aisles = [frozenset(loc.aisle for loc in o.locations) for o in instance.orders]
        cost = _Costs(instance, router, self.cache_size)
        index = {o.id: i for i, o in enumerate(instance.orders)}

        def to_solution(batches: Batches, finished: bool) -> Solution:
            ordered = sorted((sorted(b) for b in batches), key=lambda b: b[0])
            return build_solution(
                [Batch(tuple(instance.orders[i] for i in b)) for b in ordered],
                router,
                instance.layout,
                time.perf_counter() - start,
                finished,
            )

        initial = Savings().solve(instance, router, deadline, incumbent)
        if n < 2 or deadline.expired():
            return initial
        current: Batches = [frozenset(index[o.id] for o in b.orders) for b in initial.batches]
        current_cost = sum(cost(b) for b in current)
        best, best_cost = current, current_cost

        # --- destroy operators: return (kept batches, removed order indices) ---

        def pick_ranked(ranked: list[int], q: int) -> list[int]:
            ranked, chosen = list(ranked), []
            while ranked and len(chosen) < q:
                chosen.append(ranked.pop(int(rng.random() ** self.determinism * len(ranked))))
            return chosen

        def destroy_random(batches: Batches, q: int) -> list[int]:
            return rng.sample(sorted(i for b in batches for i in b), q)

        def destroy_worst(batches: Batches, q: int) -> list[int]:
            gain = {i: cost(b) - cost(b - {i}) for b in batches for i in b}
            return pick_ranked(sorted(gain, key=lambda i: (-gain[i], i)), q)

        def destroy_related(batches: Batches, q: int) -> list[int]:
            pivot = rng.randrange(n)

            def similarity(i: int) -> float:
                return len(aisles[i] & aisles[pivot]) / len(aisles[i] | aisles[pivot])

            others = sorted((i for i in range(n) if i != pivot), key=lambda i: (-similarity(i), i))
            return [pivot, *pick_ranked(others, q - 1)]

        # --- repair operators: insert every removed order, best-first by a priority rule ---

        def repair(batches: Batches, removed: list[int], regret: bool) -> Batches:
            batches = list(batches)
            loads = [sum(sizes[i] for i in b) for b in batches]
            costs = [cost(b) for b in batches]

            def delta(i: int, j: int) -> float | None:
                if loads[j] + sizes[i] > instance.capacity:
                    return None
                return cost(batches[j] | {i}) - costs[j]

            # table[i][j] = extra distance of inserting order i into batch j (fitting batches only)
            table: dict[int, dict[int, float]] = {}
            for i in removed:
                table[i] = {}
                for j in range(len(batches)):
                    d = delta(i, j)
                    if d is not None:
                        table[i][j] = d
            alone = {i: cost(frozenset((i,))) for i in removed}

            while table:
                # Lowest key wins: (-regret, cheapest insertion, order) or (cheapest, 0, order).
                choice: tuple[tuple[float, float, int], int] | None = None
                for i, row in table.items():
                    # (delta, batch); -1 means open a new batch.
                    top = heapq.nsmallest(2, [*((d, j) for j, d in row.items()), (alone[i], -1)])
                    if regret:
                        second = top[1][0] if len(top) > 1 else math.inf
                        key = (top[0][0] - second, top[0][0], i)
                    else:
                        key = (top[0][0], 0.0, i)
                    if choice is None or key < choice[0]:
                        choice = (key, top[0][1])
                assert choice is not None
                i, j = choice[0][2], choice[1]
                del table[i]
                if j == -1:
                    batches.append(frozenset((i,)))
                    loads.append(sizes[i])
                    costs.append(alone[i])
                    j = len(batches) - 1
                else:
                    batches[j] = batches[j] | {i}
                    loads[j] += sizes[i]
                    costs[j] = cost(batches[j])
                for k in table:
                    d = delta(k, j)
                    if d is None:
                        table[k].pop(j, None)
                    else:
                        table[k][j] = d
            return batches

        destroys: list[Callable[[Batches, int], list[int]]] = [
            destroy_random,
            destroy_worst,
            destroy_related,
        ]
        repairs = [False, True]  # regret flag: greedy, regret-2
        d_weights, r_weights = [1.0] * len(destroys), [1.0] * len(repairs)
        d_score, r_score = [0.0] * len(destroys), [0.0] * len(repairs)
        d_uses, r_uses = [0] * len(destroys), [0] * len(repairs)

        temperature = -self.start_worse_accept * current_cost / math.log(0.5)
        q_max = max(self.remove_min, int(self.remove_max_fraction * n))
        finished = True
        for iteration in range(1, self.max_iterations + 1):
            if deadline.expired():
                finished = False
                break
            d = rng.choices(range(len(destroys)), weights=d_weights)[0]
            r = rng.choices(range(len(repairs)), weights=r_weights)[0]
            q = min(n, rng.randint(self.remove_min, q_max))

            removed = destroys[d](current, q)
            gone = set(removed)
            kept = [b - gone for b in current]
            candidate = repair([b for b in kept if b], removed, repairs[r])
            candidate_cost = sum(cost(b) for b in candidate)

            score = 0.0
            if candidate_cost < best_cost - 1e-9:
                best, best_cost = candidate, candidate_cost
                current, current_cost = candidate, candidate_cost
                score = self.scores[0]
                if incumbent is not None:
                    incumbent.offer(to_solution(best, finished=False))
            elif candidate_cost < current_cost - 1e-9:
                current, current_cost = candidate, candidate_cost
                score = self.scores[1]
            elif rng.random() < math.exp(-(candidate_cost - current_cost) / temperature):
                current, current_cost = candidate, candidate_cost
                score = self.scores[2]
            temperature *= self.cooling

            d_score[d] += score
            r_score[r] += score
            d_uses[d] += 1
            r_uses[r] += 1
            if iteration % self.segment_length == 0:
                for weights, scores, uses in (
                    (d_weights, d_score, d_uses),
                    (r_weights, r_score, r_uses),
                ):
                    for k in range(len(weights)):
                        if uses[k]:
                            weights[k] = (1 - self.reaction) * weights[k] + self.reaction * (
                                scores[k] / uses[k]
                            )
                        # Keep every operator selectable.
                        weights[k] = max(weights[k], 1e-3)
                        scores[k], uses[k] = 0.0, 0

        solution = to_solution(best, finished)
        if incumbent is not None:
            incumbent.offer(solution)
        return solution
