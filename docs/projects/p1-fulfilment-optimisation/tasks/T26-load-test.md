# T26: Load test and documented p95

**Phase:** 6 Service · **Estimate:** 1.5 h · **Depends on:** T23, T25

## Ask

Load-test the live endpoint and document p95 latency against the budget.

## Why

"Done when" requires a documented p95. It's the evidence that the latency budget works end to end,
not just in unit tests.

## How

- Locust or k6 with a mix of request sizes from the generator.
- Report warm p50/p95/p99 separately from cold start; a few fixed concurrency levels.

## Plan

- [ ] Load-test script and request mix
- [ ] Run against Cloud Run
- [ ] Record results and a latency chart in `results/`

## Acceptance criteria

- [ ] Warm p95 is below the configured budget (+ network) at the stated concurrency
- [ ] Load test is re-runnable from one command
- [ ] Results include request mix, concurrency, p50/p95/p99 and cold-start note
