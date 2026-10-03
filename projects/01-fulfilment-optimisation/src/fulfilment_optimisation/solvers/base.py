"""The interface every batching solver implements, and the deadline and incumbent it works with.

Contract for ``Solver.solve(instance, router, deadline, incumbent)``:

- **Deadline.** The solver checks ``deadline`` itself (each iteration, or from a solution
  callback) and returns once it has expired, at most one iteration late. Nothing kills it from
  outside. Solvers that don't search (FCFS, seed, savings) may ignore it.
- **Incumbent.** Whenever the solver finds a solution better than its last one, it offers it to
  ``incumbent``. Another thread can read ``incumbent.best`` at any time, so a caller with a hard
  budget (T23) can return the best-so-far without waiting for ``solve`` to return.
- **Result.** ``solve`` returns the best solution it found. ``finished`` is True if it stopped on
  its own (search complete or nothing to search) and False if it stopped because the deadline
  expired.
"""

from __future__ import annotations

import math
import threading
import time
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from fulfilment_optimisation.domain import Batch, Instance, Layout, Route
from fulfilment_optimisation.routing import Router


@dataclass(frozen=True, slots=True)
class Deadline:
    """A point in ``time.monotonic()`` time after which a solver should stop."""

    expires_at: float

    @classmethod
    def after(cls, seconds: float) -> Deadline:
        return cls(time.monotonic() + seconds)

    @classmethod
    def never(cls) -> Deadline:
        return cls(math.inf)

    def remaining(self) -> float:
        return max(0.0, self.expires_at - time.monotonic())

    def expired(self) -> bool:
        return time.monotonic() >= self.expires_at


@dataclass(frozen=True, slots=True)
class Solution:
    batches: tuple[Batch, ...]
    routes: tuple[Route, ...]  # one per batch, same order
    total_distance: float
    solve_time: float  # seconds
    finished: bool  # False if the solver stopped at the deadline


class Incumbent:
    """Thread-safe holder for the best solution found so far (lowest total distance)."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._best: Solution | None = None

    def offer(self, solution: Solution) -> bool:
        """Keep ``solution`` if it beats the current best. Returns whether it was kept."""
        with self._lock:
            if self._best is not None and solution.total_distance >= self._best.total_distance:
                return False
            self._best = solution
            return True

    @property
    def best(self) -> Solution | None:
        with self._lock:
            return self._best


class Solver(Protocol):
    name: str

    def solve(
        self,
        instance: Instance,
        router: Router,
        deadline: Deadline,
        incumbent: Incumbent | None = None,
    ) -> Solution:
        """Batch ``instance``'s orders. See the module docstring for the deadline contract."""
        ...


def build_solution(
    batches: Iterable[Batch],
    router: Router,
    layout: Layout,
    solve_time: float,
    finished: bool,
) -> Solution:
    """Route every batch and total the distance."""
    batches = tuple(batches)
    routes = tuple(router.route(batch, layout) for batch in batches)
    return Solution(
        batches=batches,
        routes=routes,
        total_distance=sum(route.length for route in routes),
        solve_time=solve_time,
        finished=finished,
    )
