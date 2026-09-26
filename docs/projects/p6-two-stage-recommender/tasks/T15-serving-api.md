# T15: Serving API with candidate cache and online ranking

**Phase:** 5 Serving · **Estimate:** 2.5 h · **Depends on:** T09, T11

## Ask

Build a FastAPI service: `GET /recommendations/{user_id}?k=` returns top-k tracks using precomputed
candidates and online LightGBM ranking.

## Why

The second "Done when" item. Showing the two-stage split at serving time (cheap cached retrieval,
per-request ranking) is the point of the architecture.

## How

- Startup: load candidate cache (user → candidates), feature store (Parquet → in-memory), ranker.
- Request: fetch candidates, assemble features, rank, return top-k with scores.
- Unknown or cold users: fall back to recent-popular; flag it in the response.
- Cache has a build timestamp and a TTL in config; document invalidation vs freshness trade-off.
- `/health` endpoint.

## Plan

- [ ] Cache and feature loading
- [ ] Endpoint and response model
- [ ] Cold-user fallback
- [ ] Tests with `TestClient` on a small fixture

## Acceptance criteria

- [ ] Known user returns k ranked tracks matching offline ranker output for the same inputs
- [ ] Unknown user returns recent-popular with `fallback=true`
- [ ] Tests run without the full dataset
