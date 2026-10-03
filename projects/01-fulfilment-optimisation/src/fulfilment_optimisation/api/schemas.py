"""Request and response models for ``POST /batch``, and their mapping to the domain types.

The API has its own pydantic models rather than exposing the domain dataclasses, so the wire
contract can stay stable while the solvers' internals change.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from fulfilment_optimisation.domain import Instance, Layout, Location, Order
from fulfilment_optimisation.registry import ROUTERS, SOLVERS
from fulfilment_optimisation.solvers import Solution

_EXAMPLE_REQUEST = {
    "layout": "henn_waescher",
    "capacity": 6,
    "solver": "fcfs",
    "router": "s_shape",
    "budget_ms": 1000,
    "orders": [
        {"id": 1, "locations": [{"aisle": 0, "position": 3}, {"aisle": 4, "position": 20}]},
        {"id": 2, "locations": [{"aisle": 1, "position": 10, "side": 1}]},
        {"id": 3, "locations": [{"aisle": 4, "position": 2}, {"aisle": 7, "position": 40}]},
        {"id": 4, "locations": [{"aisle": 2, "position": 15}, {"aisle": 3, "position": 30}]},
    ],
}

# The service's actual response to _EXAMPLE_REQUEST (solve time rounded).
_EXAMPLE_RESPONSE = {
    "status": "finished",
    "solver": "fcfs",
    "router": "s_shape",
    "fallback_used": False,
    "total_distance": 380.0,
    "solve_time_ms": 0.003,
    "batches": [
        {
            "order_ids": [1, 2, 3],
            "items": 5,
            "route": {
                "stops": [
                    {"aisle": 0, "position": 3, "side": 0},
                    {"aisle": 1, "position": 10, "side": 1},
                    {"aisle": 4, "position": 2, "side": 0},
                    {"aisle": 4, "position": 20, "side": 0},
                    {"aisle": 7, "position": 40, "side": 0},
                ],
                "length": 256.0,
            },
        },
        {
            "order_ids": [4],
            "items": 2,
            "route": {
                "stops": [
                    {"aisle": 2, "position": 15, "side": 0},
                    {"aisle": 3, "position": 30, "side": 0},
                ],
                "length": 124.0,
            },
        },
    ],
}


class LocationIn(BaseModel):
    aisle: int = Field(ge=0)
    position: int = Field(ge=0, description="Pick position along the aisle, 0 at the front")
    side: Literal[0, 1] = Field(0, description="0 left, 1 right; doesn't change distances")


class OrderIn(BaseModel):
    id: int
    locations: list[LocationIn] = Field(min_length=1, description="One item per location")


class LayoutIn(BaseModel):
    """A single-block, parallel-aisle layout. Distances are in the layout's length units."""

    n_aisles: int = Field(ge=1)
    n_positions: int = Field(ge=1)
    location_length: float = Field(gt=0)
    aisle_spacing: float = Field(gt=0)
    end_offset: float = Field(ge=0)
    depot_offset: float = Field(ge=0)

    def to_domain(self) -> Layout:
        return Layout(**self.model_dump())


class BatchRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [_EXAMPLE_REQUEST]})

    orders: list[OrderIn] = Field(min_length=1)
    layout: LayoutIn | str = Field(
        "henn_waescher", description="A layout, or the id of a preset layout"
    )
    capacity: int = Field(ge=1, description="Items a picker can carry in one batch")
    solver: str = Field("alns", json_schema_extra={"enum": list(SOLVERS)})
    router: str = Field("s_shape", json_schema_extra={"enum": list(ROUTERS)})
    budget_ms: int = Field(
        1000,
        ge=1,
        description="Hard limit on server-side response time, in milliseconds. The best solution"
        " found within it is returned; FCFS if nothing better is ready.",
    )

    @field_validator("orders")
    @classmethod
    def _unique_ids(cls, orders: list[OrderIn]) -> list[OrderIn]:
        ids = [order.id for order in orders]
        if len(ids) != len(set(ids)):
            duplicates = sorted({i for i in ids if ids.count(i) > 1})
            raise ValueError(f"order ids must be unique; repeated: {duplicates}")
        return orders

    @field_validator("solver")
    @classmethod
    def _known_solver(cls, solver: str) -> str:
        if solver not in SOLVERS:
            raise ValueError(f"unknown solver {solver!r}; choose from {sorted(SOLVERS)}")
        return solver

    @field_validator("router")
    @classmethod
    def _known_router(cls, router: str) -> str:
        if router not in ROUTERS:
            raise ValueError(f"unknown router {router!r}; choose from {sorted(ROUTERS)}")
        return router

    def to_instance(self, layout: Layout) -> Instance:
        """Build the domain instance. Raises ``ValueError`` if an order can't be picked."""
        orders = tuple(
            Order(o.id, tuple(Location(loc.aisle, loc.position, loc.side) for loc in o.locations))
            for o in self.orders
        )
        return Instance("request", layout, orders, self.capacity)


class LocationOut(BaseModel):
    aisle: int
    position: int
    side: int


class RouteOut(BaseModel):
    stops: list[LocationOut] = Field(
        description="Visiting order; the tour starts and ends at the depot"
    )
    length: float


class BatchOut(BaseModel):
    order_ids: list[int]
    items: int
    route: RouteOut


class BatchResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"examples": [_EXAMPLE_RESPONSE]})

    status: Literal["finished", "deadline"] = Field(
        description="'deadline' if the solver was stopped by the budget"
    )
    solver: str = Field(description="Solver whose batches are returned: 'fcfs' on fallback")
    router: str
    fallback_used: bool = Field(
        description="True if FCFS was returned instead of the requested solver's result"
    )
    total_distance: float
    solve_time_ms: float
    batches: list[BatchOut]


def response_payload(
    solution: Solution,
    solver: str,
    router: str,
    fallback_used: bool = False,
    timed_out: bool = False,
) -> dict[str, Any]:
    """The ``BatchResponse`` body as plain JSON-ready data.

    Built directly rather than through the pydantic models. On a 300-order request, constructing
    about 1,000 nested models and having FastAPI re-validate them took around 45 ms on a slow CPU,
    longer than the response margin. ``tests/test_api.py`` checks the shape still validates
    against ``BatchResponse``.
    """
    return {
        "status": "deadline" if timed_out or not solution.finished else "finished",
        "solver": solver,
        "router": router,
        "fallback_used": fallback_used,
        "total_distance": solution.total_distance,
        "solve_time_ms": 1000 * solution.solve_time,
        "batches": [
            {
                "order_ids": [order.id for order in batch.orders],
                "items": batch.size,
                "route": {
                    "stops": [
                        {"aisle": s.aisle, "position": s.position, "side": s.side}
                        for s in route.stops
                    ],
                    "length": route.length,
                },
            }
            for batch, route in zip(solution.batches, solution.routes, strict=True)
        ],
    }
