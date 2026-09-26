# T10: Solver interface and greedy FCFS baseline

**Phase:** 3 Solvers · **Estimate:** 1.5 h · **Depends on:** T04, T07

## Ask

Define the batching solver interface and implement the first-come-first-served greedy baseline.

## Why

Every result is reported relative to FCFS, so it must be simple, deterministic and obviously correct.
The interface fixes how the harness and the API call every solver, including the deadline.

## How

- `Solver.solve(instance, router, deadline) -> Solution`. `Solution` holds batches, routes, total
  distance, solve time and whether it finished or hit the deadline.
- Anytime contract: solvers expose an incumbent that can be read at any time (callback or
  generator), so T23 can return the best-so-far.
- FCFS: add orders in arrival order until picker capacity is reached, then start a new batch.

## Plan

- [ ] Write `Solution` and `Solver` protocol with deadline semantics
- [ ] Implement FCFS
- [ ] Feasibility checker: every order in exactly one batch, capacity respected
- [ ] Tests

## Acceptance criteria

- [ ] FCFS output passes the feasibility checker on all Henn & Wäscher instances
- [ ] FCFS is deterministic (same input, same output)
- [ ] Interface docstring defines deadline and incumbent behaviour
