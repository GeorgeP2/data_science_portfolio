"""The interface every routing policy implements."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from typing import Protocol

from fulfilment_optimisation.domain import Batch, Layout, Location, Route


class Router(Protocol):
    name: str

    def route(self, batch: Batch, layout: Layout) -> Route:
        """The full tour: stops in visiting order and its length."""
        ...

    def length(self, locations: Iterable[Location], layout: Layout) -> float:
        """Tour length only, for solvers that just need a batch's cost."""
        ...


def picks_by_aisle(locations: Iterable[Location]) -> dict[int, list[Location]]:
    """Group picks by aisle, with aisles in left-to-right order."""
    aisles: dict[int, list[Location]] = defaultdict(list)
    for loc in locations:
        aisles[loc.aisle].append(loc)
    return dict(sorted(aisles.items()))
