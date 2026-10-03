"""FastAPI app for the batching service.

    PYTHONPATH=src uvicorn fulfilment_optimisation.api.app:app

Limits (order count, budget) and preset layouts come from the ``api`` section of
``config.yaml``. Errors return ``{"detail": "<message>"}``: 413 when a request has more orders
than the limit, 422 when it can't be solved as given (an order over capacity, a pick outside the
layout, an unknown layout id or a budget over the limit).
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException

from fulfilment_optimisation.api.schemas import BatchRequest, BatchResponse, LayoutIn
from fulfilment_optimisation.domain import Layout
from fulfilment_optimisation.registry import ROUTERS, SOLVERS
from fulfilment_optimisation.solvers import Deadline
from portfolio import ProjectPaths, load_config
from portfolio.config import Config

_ERRORS = {
    413: {"description": "More orders than the service accepts in one request"},
    422: {"description": "The request can't be solved as given; `detail` says why"},
}


def create_app(cfg: Config | None = None) -> FastAPI:
    cfg = cfg or load_config(ProjectPaths.from_file(__file__).config)
    limits = cfg.api
    presets = {name: Layout(**spec) for name, spec in limits.layouts.items()}

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

        solver = SOLVERS[request.solver](cfg.seed, cfg.solvers.get(request.solver, {}))
        router = ROUTERS[request.router]()
        solution = solver.solve(instance, router, Deadline.after(request.budget_ms / 1000))
        return BatchResponse.from_solution(solution, request.solver, request.router)

    return app


app = create_app()
