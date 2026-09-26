# T16: Load test against the latency SLO

**Phase:** 3 Streaming · **Estimate:** 1.5 h · **Depends on:** T13, T15

## Ask

Replay at several multiples of real time and report p50/p99 latency against the ≤50 ms p99 SLO.

## Why

Headline question 1 is framed at a 50 ms p99 budget; the load test is the evidence the system meets it,
and where it stops meeting it.

## How

- Sweep `N` (speed-up) until p99 breaches 50 ms or the producer saturates; repeat for in-memory and Redis.
- Latency = decision publish time − produce time, plus the per-stage breakdown.
- Record hardware, container resource limits and partition/consumer count.

## Plan

- [ ] Load-test script over a grid of `N`
- [ ] Collect latencies from the `decisions` topic
- [ ] Chart: p50/p99 vs throughput, per backend
- [ ] Results into `results/`

## Acceptance criteria

- [ ] p50 and p99 reported at each `N` for both backends, with the SLO line on the chart
- [ ] The maximum `N` meeting the SLO is stated
- [ ] Hardware and resource limits are documented
- [ ] Re-runnable from one command
