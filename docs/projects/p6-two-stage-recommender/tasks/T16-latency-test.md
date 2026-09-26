# T16: p95 latency test

**Phase:** 5 Serving · **Estimate:** 1 h · **Depends on:** T15

## Ask

Load-test the serving API and report p50/p95 latency, broken down by stage.

## Why

The brief requires a p95 latency test. The per-stage breakdown backs the "why two stages" write-up.

## How

- Locust or k6 against the local container, with users sampled from the test set.
- Server-side timing per stage (cache lookup, feature assembly, ranking) via logs or headers.
- Latency target in `config.yaml`.

## Plan

- [ ] Load-test script
- [ ] Per-stage timing
- [ ] Results note with a chart

## Acceptance criteria

- [ ] p50/p95/p99 reported at a stated concurrency
- [ ] Per-stage p95 reported
- [ ] Test re-runs from one command
