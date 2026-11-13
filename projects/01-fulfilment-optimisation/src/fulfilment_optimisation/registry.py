"""Solvers and routers by name, as used in ``config.yaml`` and API requests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any

from fulfilment_optimisation.routing import LargestGap, Optimal, Router, SShape
from fulfilment_optimisation.solvers import (
    ALNS,
    FCFS,
    Savings,
    SeedBatching,
    Solver,
)

# A factory takes the run's seed (for stochastic solvers) and the solver's ``solvers.<name>``
# section of config.yaml.
SolverFactory = Callable[[int, Mapping[str, Any]], Solver]


def _fcfs(seed: int, params: Mapping[str, Any]) -> Solver:
    return FCFS()


def _seed(seed: int, params: Mapping[str, Any]) -> Solver:
    return SeedBatching(**params)


def _savings(seed: int, params: Mapping[str, Any]) -> Solver:
    return Savings()


def _alns(seed: int, params: Mapping[str, Any]) -> Solver:
    return ALNS(seed=seed, **params)


def _cp_sat(seed: int, params: Mapping[str, Any]) -> Solver:
    # Imported here so the rest of the package (and the service image) works without OR-Tools.
    from fulfilment_optimisation.solvers.cp_sat import CPSATBatching

    return CPSATBatching(seed=seed, **params)


def _ortools(seed: int, params: Mapping[str, Any]) -> Solver:
    # Deterministic for a given time limit, so the seed is unused.
    from fulfilment_optimisation.solvers.ortools_routing import ORToolsRouting

    return ORToolsRouting(**params)


SOLVERS: dict[str, SolverFactory] = {
    "fcfs": _fcfs,
    "seed": _seed,
    "savings": _savings,
    "alns": _alns,
    "cp_sat": _cp_sat,
    "ortools": _ortools,
}
ROUTERS: dict[str, Callable[[], Router]] = {
    "s_shape": SShape,
    "largest_gap": LargestGap,
    "optimal": Optimal,
}
