"""Solvers and routers by name, as used in ``config.yaml`` and API requests."""

from __future__ import annotations

from collections.abc import Callable

from fulfilment_optimisation.routing import LargestGap, Router, SShape
from fulfilment_optimisation.solvers import FCFS, Solver


def _fcfs(seed: int) -> Solver:
    return FCFS()


# Factories take a seed, so stochastic solvers can be seeded per run.
SOLVERS: dict[str, Callable[[int], Solver]] = {"fcfs": _fcfs}
ROUTERS: dict[str, Callable[[], Router]] = {"s_shape": SShape, "largest_gap": LargestGap}
