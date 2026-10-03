"""FastAPI app for the batching service.

    PYTHONPATH=src uvicorn fulfilment_optimisation.api.app:app

``budget_ms`` is a hard limit on server-side response time: the solver runs under it and the best
solution found in time is returned, with FCFS as the fallback (see ``api.runner``). Limits, the
response margin, worker threads and preset layouts come from the ``api`` section of
``config.yaml``. Errors return ``{"detail": "<message>"}``: 413 when a request has more orders
than the limit, 422 when it can't be solved as given (an order over capacity, a pick outside the
layout, an unknown layout id or a budget over the limit).
"""

from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor

from fastapi import FastAPI, HTTPException

from fulfilment_optimisation.api.runner import run_with_budget
from fulfilment_optimisation.api.schemas import BatchRequest, BatchResponse, LayoutIn
from fulfilment_optimisation.domain import Layout
from fulfilment_optimisation.registry import ROUTERS, SOLVERS, SolverFactory
from portfolio import ProjectPaths, load_config
from portfolio.config import Config

_ERRORS = {
    413: {"description": "More orders than the service accepts in one request"},
    422: {"description": "The request can't be solved as given; `detail` says why"},
}


def create_app(
    cfg: Config | None = None, solvers: Mapping[str, SolverFactory] = SOLVERS
) -> FastAPI:
    """``solvers`` is overridable so tests can add deliberately slow or failing solvers."""
    cfg = cfg or load_config(ProjectPaths.from_file(__file__).config)
    limits = cfg.api
    presets = {name: Layout(**spec) for name, spec in limits.layouts.items()}
    executor = ThreadPoolExecutor(max_workers=limits.solver_threads, thread_name_prefix="solver")

    app = FastAPI(
        title="Fulfilment Optimisation Service",
        description="Order batching and picker routing for single-block warehouses.",
        version="0.1.0",
    )

    def resolve_layout(layout: LayoutIn | str) -> Layout:
        if isinstance(layout, LayoutIn):
            return layout.to_domain()
        if layout not in presets:
            raise HTTPException(422, f"unknown layout {layout!r}; choose from {sorted(presets)}")
        return presets[layout]

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/batch", responses=_ERRORS)  # type: ignore[arg-type]
    def batch(request: BatchRequest) -> BatchResponse:
        if len(request.orders) > limits.max_orders:
            raise HTTPException(
                413, f"{len(request.orders)} orders; the limit is {limits.max_orders} per request"
            )
        if request.budget_ms > limits.max_budget_ms:
            raise HTTPException(
                422, f"budget_ms {request.budget_ms} is over the limit of {limits.max_budget_ms}"
            )
        try:
            instance = request.to_instance(resolve_layout(request.layout))
        except ValueError as e:
            raise HTTPException(422, str(e).removeprefix("request: ")) from e

        solver = solvers[request.solver](cfg.seed, cfg.solvers.get(request.solver, {}))
        result = run_with_budget(
            instance,
            solver,
            ROUTERS[request.router](),
            budget_s=request.budget_ms / 1000,
            margin_s=limits.response_margin_ms / 1000,
            executor=executor,
        )
        return BatchResponse.from_solution(
            result.solution,
            result.solver,
            request.router,
            fallback_used=result.fallback_used,
            timed_out=result.timed_out,
        )

    return app


app = create_app()
