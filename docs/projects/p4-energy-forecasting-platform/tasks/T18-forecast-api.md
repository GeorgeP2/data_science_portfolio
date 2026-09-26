# T18: FastAPI `/forecast` endpoint

**Phase:** 4 Platform · **Estimate:** 1.5 h · **Depends on:** T14

## Ask

Serve the production national model through a FastAPI `/forecast` endpoint that returns quantile
forecasts for a requested day.

## Why

The brief requires both models to be served. The endpoint is also the data source for the dashboard.

## How

- `GET /forecast?date=YYYY-MM-DD` returns the settlement periods for that day with quantiles, the
  model version and the issue time. Serve the household model's forecasts from precomputed outputs
  if serving it live is too slow (e.g. `GET /forecast/household/{id}`).
- Loads the model via the `production` alias at startup; `/health` endpoint.
- 404 for dates with no inputs yet; 422 for malformed dates.

## Plan

- [ ] Response schema
- [ ] National endpoint
- [ ] Household endpoint (precomputed if needed)
- [ ] Error cases
- [ ] Tests with `TestClient` and a stub model

## Acceptance criteria

- [ ] Response for a valid date contains every settlement period of that day (46/48/50) with ordered quantiles
- [ ] Model version in the response matches the MLflow `production` alias
- [ ] Error paths are tested
