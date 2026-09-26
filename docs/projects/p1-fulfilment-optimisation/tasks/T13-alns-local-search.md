# T13: ALNS local search

**Phase:** 3 Solvers · **Estimate:** 4 h · **Depends on:** T10, T11

## Ask

Implement my own adaptive large neighbourhood search for order batching.

## Why

A hand-written metaheuristic is the core algorithmic contribution. ALNS is naturally anytime, which
suits a latency-budgeted API.

## How

- Destroy operators: random, worst (highest marginal distance), related (shared aisles).
- Repair operators: greedy insertion, regret-k insertion; all respect capacity.
- Adaptive operator weights, simulated-annealing acceptance; parameters in `config.yaml`.
- Start from savings; keep the incumbent readable at any time; stop at the deadline.
- Cache batch route lengths, as routing dominates run time.

## Plan

- [ ] Skeleton loop with deadline and incumbent
- [ ] Destroy operators
- [ ] Repair operators
- [ ] Weight adaptation and acceptance
- [ ] Route-length cache
- [ ] Seeded tests

## Acceptance criteria

- [ ] Every returned solution passes the feasibility checker
- [ ] Deterministic for a fixed seed
- [ ] Beats savings on average across Henn & Wäscher at a 1 s budget
- [ ] Stops within 50 ms of the deadline
