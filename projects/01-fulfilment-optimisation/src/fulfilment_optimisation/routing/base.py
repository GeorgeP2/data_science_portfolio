"""The interface every routing policy implements."""

from __future__ import annotations

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
