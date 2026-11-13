"""Order batching as a capacitated vehicle routing problem, solved with OR-Tools' routing library.

A practitioner baseline: the routing solver most engineers would reach for first. Each vehicle is
one picker tour with capacity in items, so the orders on a vehicle are a batch. Arc costs are
``domain.distance`` times ``cost_scale``, rounded, because OR-Tools needs integers. Unused vehicles
cost nothing; there are as many as the warm start has batches, plus ``spare_vehicles``.

**Models** (``model``):

- ``pick_nodes``: one node per pick (order, location), demand 1, and every pick of an order on the
  same vehicle (``VehicleVar(a) == VehicleVar(b)``). A vehicle's cost is then a travelling-salesman
  tour through its picks, the quantity optimal routing computes. The most faithful model, but it
  barely re-batches: OR-Tools' local search moves one node (or a chain of consecutive nodes) at a
  time, and moving one pick of a multi-pick order breaks the same-vehicle constraint, so almost
  only within-tour moves are accepted. On the Henn & Wäscher instances (4-24 picks per order) it
  returned the savings batches in all 384 benchmark runs. Without the warm start, OR-Tools'
  default first-solution heuristic found no feasible solution within 1 s on a 40-order instance.
- ``order_nodes`` (the default): one node per order, placed at its centre of gravity (mean aisle
  and mean position, rounded to a location), with demand equal to its size. A cheaper
  approximation and a common practitioner baseline: the tour cost between orders ignores how far
  each order's picks spread.

Whatever the model's own objective says, the batches are **re-scored with the run's router**
(S-shape, largest gap or optimal), like every other solver.

**Search.** The savings solution (costed with the run's router) is the starting point: its batches
are read in as routes, each in its router's visiting order (an order goes where its first pick is
visited). ``metaheuristic`` (guided local search by default) then runs until the deadline less
``deadline_margin``, through ``search_parameters.time_limit``. With no deadline it stops at the
first local optimum (greedy descent) instead, since guided local search never stops on its own.
Every solution that improves the model's objective is re-scored and offered to the incumbent.

**Result.** The search's final solution, re-scored: what OR-Tools hands a practitioner. Unlike
CP-SAT, it doesn't fall back to its warm start when that scores better under the run's router,
since that would turn the baseline into savings; with order nodes it usually is worse, because the
model's objective isn't the router's. The incumbent sees the same: only solutions the search
reports, never the savings start on its own (unless the deadline leaves no time to search, when
savings is returned). ``finished`` is True only when the search stopped on its own (no deadline).
"""

from __future__ import annotations

import time
from collections.abc import Sequence
from statistics import fmean

from ortools.constraint_solver import pywrapcp, routing_enums_pb2

from fulfilment_optimisation.domain import DEPOT, Batch, Instance, Location, Order, Point, distance
from fulfilment_optimisation.routing import Router
from fulfilment_optimisation.solvers.base import Deadline, Incumbent, Solution, build_solution
from fulfilment_optimisation.solvers.savings import Savings

MODELS = ("order_nodes", "pick_nodes")


def _metaheuristic(name: str) -> int:
    try:
        return getattr(routing_enums_pb2.LocalSearchMetaheuristic, name)
    except AttributeError:
        raise ValueError(f"unknown OR-Tools metaheuristic {name!r}") from None


def centre_of_gravity(order: Order) -> Location:
    """The location at the order's mean aisle and mean position, rounded."""
    return Location(
        round(fmean(loc.aisle for loc in order.locations)),
        round(fmean(loc.position for loc in order.locations)),
    )


class ORToolsRouting:
    name = "ortools"

    def __init__(
        self,
        model: str = "order_nodes",
        cost_scale: int = 10,
        spare_vehicles: int = 2,
        metaheuristic: str = "GUIDED_LOCAL_SEARCH",
        deadline_margin: float = 0.02,
    ) -> None:
        if model not in MODELS:
            raise ValueError(f"unknown model {model!r}; choose from {MODELS}")
        _metaheuristic(metaheuristic)
        self.model = model
        self.cost_scale = cost_scale
        self.spare_vehicles = spare_vehicles
        self.metaheuristic = metaheuristic
        self.deadline_margin = deadline_margin
        # The model's own objective for the last solve's result, in LU (None if no search ran).
        # For pick nodes it's the sum of OR-Tools' tours, which tests compare with optimal routing.
        self.model_cost: float | None = None

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        start = time.perf_counter()
        layout = instance.layout
        self.model_cost = None

        def to_solution(batches: Sequence[Sequence[int]], finished: bool) -> Solution:
            ordered = sorted((sorted(b) for b in batches if b), key=lambda b: b[0])
            return build_solution(
                [Batch(tuple(instance.orders[i] for i in b)) for b in ordered],
                router,
                layout,
                time.perf_counter() - start,
                finished,
            )

        warm = Savings().solve(instance, router, deadline)
        index = {o.id: i for i, o in enumerate(instance.orders)}
        warm_batches = [[index[o.id] for o in b.orders] for b in warm.batches]
        no_deadline = deadline.expires_at == float("inf")

        def no_search() -> Solution:
            """The savings start, when there's no time (or no result) from the search."""
            solution = to_solution(warm_batches, finished=False)
            if incumbent is not None:
                incumbent.offer(solution)
            return solution

        if deadline.remaining() <= self.deadline_margin:
            return no_search()

        # --- nodes: node 0 is the depot ---
        # Each other node belongs to one order, sits at one point and covers some of the order's
        # picks (one for pick nodes, all of them for order nodes).
        node_order: list[int] = [-1]
        node_point: list[Point] = [DEPOT]
        node_picks: list[tuple[Location, ...]] = [()]
        for i, order in enumerate(instance.orders):
            if self.model == "pick_nodes":
                for loc in order.locations:
                    node_order.append(i)
                    node_point.append(loc)
                    node_picks.append((loc,))
            else:
                node_order.append(i)
                node_point.append(centre_of_gravity(order))
                node_picks.append(order.locations)
        nodes_of: list[list[int]] = [[] for _ in instance.orders]
        for node in range(1, len(node_order)):
            nodes_of[node_order[node]].append(node)

        # Arc costs, computed once per distinct point (side doesn't change distances).
        points: dict[tuple[int, int] | None, int] = {}
        coords: list[Point] = []
        point_of: list[int] = []
        for point in node_point:
            key = None if point == DEPOT else _key(point)
            if key not in points:
                points[key] = len(coords)
                coords.append(point)
            point_of.append(points[key])
        cost = [[round(self.cost_scale * distance(a, b, layout)) for b in coords] for a in coords]
        matrix = [[cost[a][b] for b in point_of] for a in point_of]

        n_nodes = len(node_order)
        n_vehicles = len(warm_batches) + self.spare_vehicles
        manager = pywrapcp.RoutingIndexManager(n_nodes, n_vehicles, 0)
        routing = pywrapcp.RoutingModel(manager)
        arc = routing.RegisterTransitMatrix(matrix)
        routing.SetArcCostEvaluatorOfAllVehicles(arc)
        demand = routing.RegisterUnaryTransitVector([len(picks) for picks in node_picks])
        routing.AddDimensionWithVehicleCapacity(
            demand, 0, [instance.capacity] * n_vehicles, True, "items"
        )
        cp_solver = routing.solver()
        for nodes in nodes_of:  # all of an order's nodes on one vehicle
            first = routing.VehicleVar(manager.NodeToIndex(nodes[0]))
            for node in nodes[1:]:
                cp_solver.Add(first == routing.VehicleVar(manager.NodeToIndex(node)))

        params = pywrapcp.DefaultRoutingSearchParameters()
        params.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GREEDY_DESCENT
            if no_deadline
            else _metaheuristic(self.metaheuristic)
        )
        if not no_deadline:
            remaining = deadline.remaining() - self.deadline_margin
            if remaining <= 0:
                return no_search()
            params.time_limit.FromMilliseconds(max(1, int(1000 * remaining)))
        routing.CloseModelWithParameters(params)

        def batches_of(value) -> list[list[int]]:
            """Order indices on each vehicle, read through ``value(NextVar)``."""
            batches = []
            for v in range(n_vehicles):
                orders: list[int] = []
                idx = value(routing.NextVar(routing.Start(v)))
                while not routing.IsEnd(idx):
                    i = node_order[manager.IndexToNode(idx)]
                    if i not in orders:
                        orders.append(i)
                    idx = value(routing.NextVar(idx))
                batches.append(orders)
            return batches

        best_cost = [float("inf")]

        def on_solution() -> None:
            objective = routing.CostVar().Value()
            if incumbent is None or objective >= best_cost[0]:
                return
            best_cost[0] = objective
            incumbent.offer(to_solution(batches_of(lambda var: var.Value()), finished=False))

        routing.AddAtSolutionCallback(on_solution)

        # Warm start: each savings batch's nodes in its router's visiting order (a node goes
        # where the first of its picks is visited).
        routes: list[list[int]] = []
        for batch, route in zip(warm_batches, warm.routes, strict=True):
            rank = {_key(loc): k for k, loc in enumerate(route.stops)}
            nodes = [node for i in batch for node in nodes_of[i]]
            routes.append(
                sorted(nodes, key=lambda n: min(rank[_key(loc)] for loc in node_picks[n]))
            )
        routes += [[] for _ in range(self.spare_vehicles)]
        initial = routing.ReadAssignmentFromRoutes(routes, True)
        if initial is None:
            raise RuntimeError(f"{instance.name}: OR-Tools rejected the savings warm start")
        assignment = routing.SolveFromAssignmentWithParameters(initial, params)
        if assignment is None:
            return no_search()

        self.model_cost = assignment.ObjectiveValue() / self.cost_scale
        solution = to_solution(batches_of(assignment.Value), finished=no_deadline)
        if incumbent is not None:
            incumbent.offer(solution)
        return solution


def _key(point: Point) -> tuple[int, int]:
    assert isinstance(point, Location)
    return (point.aisle, point.position)
