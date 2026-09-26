# T23: Latency budget and anytime fallback

**Phase:** 6 Service · **Estimate:** 2 h · **Depends on:** T12, T13, T22

## Ask

Make `budget_ms` a hard limit: run the chosen solver under the budget and return the best solution
found so far, or FCFS if none exists in time.

## Why

This is the service's distinctive feature and the basis of the "anytime algorithms" write-up.

## How

- Compute FCFS first (cheap), then run the chosen solver with deadline = budget minus a safety margin
  for serialisation.
- Run solvers in a worker process/thread so the request handler can stop waiting at the deadline.
- Return the incumbent; set `fallback_used` and `status` accordingly.

## Plan

- [ ] Deadline plumbing from request to solver
- [ ] Worker execution with timeout
- [ ] Fallback logic
- [ ] Tests with a deliberately slow solver

## Acceptance criteria

- [ ] Server-side response time ≤ `budget_ms` + margin for ≥ 99% of test requests
- [ ] With a tiny budget the response is FCFS and `fallback_used=true`
- [ ] With a generous budget the response is never worse than FCFS
