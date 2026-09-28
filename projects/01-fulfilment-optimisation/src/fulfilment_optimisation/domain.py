"""Core types and the travel distance for a single-block, parallel-aisle warehouse.

Geometry follows Henn & Wäscher (2012), section 6.1, so distances are comparable with the
published instances:

- Aisles run vertically between a front and a back cross aisle, with centres ``aisle_spacing``
  apart (5 LU). Aisle 0 is the leftmost.
- Picking is two-sided: the picker walks the aisle centre line and reaches both sides without
  extra movement, so ``Location.side`` doesn't change distances.
- Pick positions are ``location_length`` apart (1 LU) along the aisle. The picker stands at the
  front middle of a location, and the first and last positions are ``end_offset`` (1 LU) from the
  front and back cross aisles.
- The depot sits in front of aisle 0, ``depot_offset`` in front of the front cross aisle. The paper
  says 0.5 LU (1.5 LU from the depot to aisle 0's first location), but the OBSP setting files say
  ``dis_ais_wa: 1``; the parser picks the value that reproduces the published results.

All distances are in the layout's length units (LU). Coordinates put the front cross aisle at
``y = 0`` and aisle 0 at ``x = 0``.

Henn, S., Wäscher, G. (2012). Tabu search heuristics for the order batching problem in manual
order picking systems. *EJOR* 222(3), 484-494 (working paper: FEMM 07/2010, OvGU Magdeburg).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Layout:
    n_aisles: int
    n_positions: int  # pick positions along each aisle
    location_length: float
    aisle_spacing: float
    end_offset: float
    depot_offset: float

    def __post_init__(self) -> None:
        if self.n_aisles < 1 or self.n_positions < 1:
            raise ValueError("a layout needs at least one aisle and one position")

    @property
    def aisle_length(self) -> float:
        """Distance from the front cross aisle to the back cross aisle along an aisle."""
        return 2 * self.end_offset + (self.n_positions - 1) * self.location_length

    def x(self, aisle: int) -> float:
        return aisle * self.aisle_spacing

    def y(self, position: int) -> float:
        return self.end_offset + position * self.location_length

    def contains(self, location: Location) -> bool:
        return 0 <= location.aisle < self.n_aisles and 0 <= location.position < self.n_positions


@dataclass(frozen=True, slots=True, order=True)
class Location:
    aisle: int
    position: int
    side: int = 0  # 0 left, 1 right


@dataclass(frozen=True, slots=True)
class Depot:
    pass


DEPOT = Depot()
Point = Location | Depot


@dataclass(frozen=True, slots=True)
class Order:
    id: int
    locations: tuple[Location, ...]
    due_date: float | None = None

    @property
    def size(self) -> int:
        """Capacity used, in items (one item per location, as in the benchmarks)."""
        return len(self.locations)


@dataclass(frozen=True, slots=True)
class Batch:
    orders: tuple[Order, ...]

    @property
    def size(self) -> int:
        return sum(order.size for order in self.orders)

    @property
    def locations(self) -> frozenset[Location]:
        return frozenset(loc for order in self.orders for loc in order.locations)


@dataclass(frozen=True, slots=True)
class Route:
    """A picker tour for one batch: depot, ``stops`` in visiting order, depot."""

    batch: Batch
    stops: tuple[Location, ...]
    length: float


@dataclass(frozen=True, slots=True)
class Instance:
    name: str
    layout: Layout
    orders: tuple[Order, ...]
    capacity: int  # items per batch

    def __post_init__(self) -> None:
        for order in self.orders:
            if order.size > self.capacity:
                raise ValueError(f"{self.name}: order {order.id} exceeds capacity {self.capacity}")
            for loc in order.locations:
                if not self.layout.contains(loc):
                    raise ValueError(f"{self.name}: order {order.id} has {loc} outside the layout")


def distance(a: Point, b: Point, layout: Layout) -> float:
    """Shortest walking distance between two points.

    Within an aisle the picker walks straight. Between aisles they leave through whichever cross
    aisle (front or back) is shorter. The depot connects to the front cross aisle.
    """
    if isinstance(a, Depot) or isinstance(b, Depot):
        other = b if isinstance(a, Depot) else a
        if isinstance(other, Depot):
            return 0.0
        return layout.depot_offset + layout.x(other.aisle) + layout.y(other.position)

    ya, yb = layout.y(a.position), layout.y(b.position)
    if a.aisle == b.aisle:
        return abs(ya - yb)
    across = abs(layout.x(a.aisle) - layout.x(b.aisle))
    via_front = ya + yb
    via_back = 2 * layout.aisle_length - ya - yb
    return across + min(via_front, via_back)
