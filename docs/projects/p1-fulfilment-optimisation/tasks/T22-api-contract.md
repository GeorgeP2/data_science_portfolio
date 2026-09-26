# T22: FastAPI `POST /batch` contract

**Phase:** 6 Service · **Estimate:** 1.5 h · **Depends on:** T10

## Ask

Implement `POST /batch`: accepts a layout (or layout id) and orders, returns batches and routes.
Define and handle infeasible and oversized requests.

## Why

The API contract is a design decision to write up, and the service is what makes the project
"production-shaped" rather than a notebook.

## How

- Pydantic request/response models mapped to the domain types.
- Request fields: orders, layout, capacity, `solver`, `router`, `budget_ms`.
- Response: batches, routes, total distance, solver used, solve time, `fallback_used`, `status`.
- Errors: 422 for invalid input (e.g. order larger than capacity), 413 for requests over the order
  limit (set in `config.yaml`); each with a clear message.
- `/health` endpoint.

## Plan

- [ ] Request/response models
- [ ] Endpoint wired to FCFS first
- [ ] Validation and error cases
- [ ] Endpoint tests with `TestClient`

## Acceptance criteria

- [ ] Valid request returns feasible batches and routes
- [ ] Oversized request returns 413; infeasible order returns 422; both with a message
- [ ] OpenAPI docs show example request/response
- [ ] Tests cover success and each error path
