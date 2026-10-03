"""Optimal routing for a single-block warehouse: Ratliff & Rosenthal's dynamic programme.

The warehouse is a graph: in each aisle ``j`` a front node ``a_j`` (front cross aisle), a back node
``b_j`` (back cross aisle) and the pick positions between them; cross-aisle edges join neighbouring
``a`` nodes and neighbouring ``b`` nodes; the depot hangs off ``a_0`` by ``depot_offset``. A tour is
a sub-multigraph (each edge used 0, 1 or 2 times) that touches every pick and the depot, has even
degree everywhere, and is connected. The shortest such sub-graph is the optimal tour.

The DP sweeps aisles left to right. After aisle ``j`` the state records, for ``a_j`` and ``b_j``,
whether each has degree 0, odd or even (> 0), and whether they are in the same component. Every
component must still touch ``a_j`` or ``b_j``, unless the tour is already complete (``CLOSED``).
These are the paper's equivalence classes:

    (odd, odd, same)  (even, 0, -)  (0, even, -)  (even, even, same)  (even, even, separate)
    (0, 0, closed)

(The paper's seventh, the empty partial tour, can't occur here: the depot's component starts at
``a_0``.)

Each step adds, between aisles ``j-1`` and ``j``, 0, 1 or 2 copies of the front and of the back
cross-aisle edge, then one of these configurations inside aisle ``j``:

    none     no edges (only if the aisle has no picks)
    full1    walk the aisle end to end once            a +1, b +1, joins a and b
    full2    walk it end to end twice                  a +2, b +2, joins a and b
    front    in from the front to the deepest pick     a +2
    back     in from the back to the shallowest pick   b +2
    gap      split at the largest gap between picks    a +2, b +2  (each side in and back)

Rather than hard-coding the paper's transition table, each transition is checked with a small
union-find over the four frontier nodes (``a_{j-1}``, ``b_{j-1}``, ``a_j``, ``b_j``): a node leaving
the frontier must have even degree, and a component that no longer touches the frontier closes
the tour, which is only valid if it's the only component and nothing further is added.

``route`` rebuilds the chosen sub-graph and walks it with Hierholzer's algorithm from the depot;
stops are listed in first-visit order.

Ratliff, H. D., Rosenthal, A. S. (1983). Order-picking in a rectangular warehouse: a solvable
case of the traveling salesman problem. *Operations Research* 31(3), 507-521.
"""

from __future__ import annotations

import itertools
from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass
from functools import cache

from fulfilment_optimisation.domain import Batch, Layout, Location, Route

ZERO, ODD, EVEN = 0, 1, 2
CLOSED = (ZERO, ZERO, "closed")

State = tuple[int, int, str]  # (class of a, class of b, "same" | "separate" | "single" | "closed")


@dataclass(frozen=True, slots=True)
class _Config:
    name: str
    cost: float
    da: int  # degree added to the front node
    db: int  # degree added to the back node
    joins: bool  # connects front and back nodes
    cut: int = -1  # for "gap": index of the last pick reached from the front


_Pointer = tuple["State | None", int, int, _Config]  # (previous state, front, back, config)


def _add(cls: int, k: int) -> int:
    """Degree class after adding ``k`` to a node of class ``cls``."""
    if k == 0:
        return cls
    if cls == ZERO:
        return ODD if k % 2 else EVEN
    if k % 2 == 0:
        return cls
    return EVEN if cls == ODD else ODD


def _configs(depths: list[float], aisle_length: float) -> list[_Config]:
    """Ways to cover one aisle's picks (depths ascending, measured from the front)."""
    configs = [
        _Config("full1", aisle_length, 1, 1, True),
        _Config("full2", 2 * aisle_length, 2, 2, True),
    ]
    if not depths:
        return [_Config("none", 0.0, 0, 0, False), *configs]
    configs += [
        _Config("front", 2 * depths[-1], 2, 0, False),
        _Config("back", 2 * (aisle_length - depths[0]), 0, 2, False),
    ]
    if len(depths) > 1:
        k = max(range(len(depths) - 1), key=lambda i: (depths[i + 1] - depths[i], -i))
        cost = 2 * depths[k] + 2 * (aisle_length - depths[k + 1])
        configs.append(_Config("gap", cost, 2, 2, False, cut=k))
    return configs


class _UnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}

    def find(self, x: str) -> str:
        self.parent.setdefault(x, x)
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, x: str, y: str) -> None:
        self.parent[self.find(x)] = self.find(y)


@cache
def _moves(
    state: State, da: int, db: int, joins: bool, empty: bool
) -> tuple[tuple[int, int, State], ...]:
    """Valid (front copies, back copies, next state) for one aisle configuration."""
    moves = []
    for front in (0, 1, 2):
        for back in (0, 1, 2):
            new = _transition(state, front, back, da, db, joins, empty)
            if new is not None:
                moves.append((front, back, new))
    return tuple(moves)


@cache
def _transition(
    state: State, front: int, back: int, da: int, db: int, joins: bool, empty: bool
) -> State | None:
    # Only a few hundred distinct inputs exist, so each is worked out once and cached.
    if state == CLOSED:
        ok = front == back == 0 and empty
        return CLOSED if ok else None

    old_a, old_b = _add(state[0], front), _add(state[1], back)
    if old_a == ODD or old_b == ODD:
        return None  # a node leaving the frontier must have even degree
    new_a = _add(_add(ZERO, front), da)
    new_b = _add(_add(ZERO, back), db)

    uf = _UnionFind()
    if state[2] == "same":
        uf.union("a0", "b0")
    if front:
        uf.union("a0", "a1")
    if back:
        uf.union("b0", "b1")
    if joins:
        uf.union("a1", "b1")

    old = {uf.find(n) for n, cls in (("a0", state[0]), ("b0", state[1])) if cls != ZERO}
    frontier = {uf.find(n) for n, cls in (("a1", new_a), ("b1", new_b)) if cls != ZERO}
    if old - frontier:
        # A component no longer reaches the frontier: the tour is complete, which is only valid
        # if it was the only component and nothing else is on the frontier.
        return CLOSED if len(old) == 1 and not frontier else None

    if new_a != ZERO and new_b != ZERO:
        link = "same" if uf.find("a1") == uf.find("b1") else "separate"
    else:
        link = "single"
    return (new_a, new_b, link)


def _final(state: State) -> bool:
    if state == CLOSED:
        return True
    return ODD not in state[:2] and state[2] != "separate"


class Optimal:
    name = "optimal"

    def _solve(
        self, locations: Iterable[Location], layout: Layout
    ) -> tuple[float, State | None, list[dict[State, _Pointer]], list[list[float]]]:
        """Optimal length, final state, back-pointers per aisle, and pick depths per aisle."""
        depths_by_aisle: dict[int, set[float]] = defaultdict(set)
        for loc in locations:
            depths_by_aisle[loc.aisle].add(layout.y(loc.position))
        if not depths_by_aisle:
            return 0.0, None, [], []
        last = max(depths_by_aisle)
        depths = [sorted(depths_by_aisle.get(j, ())) for j in range(last + 1)]
        length = layout.aisle_length

        # Aisle 0: the depot's doubled edge gives a_0 degree 2 before anything else.
        costs: dict[State, float] = {}
        back_ptrs: list[dict[State, _Pointer]] = [{}]
        for config in _configs(depths[0], length):
            new_a, new_b = _add(EVEN, config.da), _add(ZERO, config.db)
            if new_b == ZERO:
                state: State = (new_a, new_b, "single")
            else:
                state = (new_a, new_b, "same" if config.joins else "separate")
            cost = 2 * layout.depot_offset + config.cost
            if cost < costs.get(state, float("inf")):
                costs[state] = cost
                back_ptrs[0][state] = (None, 0, 0, config)

        spacing = layout.aisle_spacing
        for j in range(1, last + 1):
            nxt: dict[State, float] = {}
            ptrs: dict[State, _Pointer] = {}
            configs = _configs(depths[j], length)
            for state, cost in costs.items():
                for config in configs:
                    key = (state, config.da, config.db, config.joins, config.name == "none")
                    for front, back, new in _moves(*key):
                        total = cost + (front + back) * spacing + config.cost
                        if total < nxt.get(new, float("inf")):
                            nxt[new] = total
                            ptrs[new] = (state, front, back, config)
            costs = nxt
            back_ptrs.append(ptrs)

        cost, best = min((c, s) for s, c in costs.items() if _final(s))
        return cost, best, back_ptrs, depths

    def length(self, locations: Iterable[Location], layout: Layout) -> float:
        return self._solve(locations, layout)[0]

    def route(self, batch: Batch, layout: Layout) -> Route:
        total, state, back_ptrs, depths = self._solve(batch.locations, layout)
        if not back_ptrs:
            return Route(batch, (), 0.0)

        # Rebuild the chosen edges: (node, node) pairs, with repeats for doubled edges.
        edges: list[tuple[tuple, tuple]] = [(("depot",), ("a", 0))] * 2
        for j in range(len(back_ptrs) - 1, -1, -1):
            assert state is not None
            prev, front, back, config = back_ptrs[j][state]
            edges += [(("a", j - 1), ("a", j))] * front + [(("b", j - 1), ("b", j))] * back
            edges += _aisle_edges(j, depths[j], config)
            state = prev

        # Hierholzer's algorithm from the depot.
        adjacency: dict[tuple, list[tuple]] = defaultdict(list)
        for u, v in edges:
            adjacency[u].append(v)
            adjacency[v].append(u)
        stack, walk = [("depot",)], []
        while stack:
            node = stack[-1]
            if adjacency[node]:
                other = adjacency[node].pop()
                adjacency[other].remove(node)
                stack.append(other)
            else:
                walk.append(stack.pop())

        by_point: dict[tuple[int, float], list[Location]] = defaultdict(list)
        for loc in batch.locations:
            by_point[(loc.aisle, layout.y(loc.position))].append(loc)
        stops: list[Location] = []
        seen: set[tuple[int, float]] = set()
        for node in walk:
            if node[0] == "p" and node[1:] not in seen:
                seen.add(node[1:])
                stops.extend(sorted(by_point[node[1:]]))
        return Route(batch, tuple(stops), total)


def _aisle_edges(j: int, depths: list[float], config: _Config) -> list[tuple[tuple, tuple]]:
    """The vertical edges ``config`` uses in aisle ``j``."""
    front, back = ("a", j), ("b", j)
    points = [("p", j, d) for d in depths]

    def path(nodes: list[tuple], times: int) -> list[tuple[tuple, tuple]]:
        return list(itertools.pairwise(nodes)) * times

    if config.name == "none":
        return []
    if config.name == "full1":
        return path([front, *points, back], 1)
    if config.name == "full2":
        return path([front, *points, back], 2)
    if config.name == "front":
        return path([front, *points], 2)
    if config.name == "back":
        return path([back, *reversed(points)], 2)
    # gap: picks up to the cut from the front, the rest from the back
    below, above = points[: config.cut + 1], points[config.cut + 1 :]
    return path([front, *below], 2) + path([back, *reversed(above)], 2)
