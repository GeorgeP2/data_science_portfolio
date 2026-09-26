# T29 (stretch): Shift simulation with dynamic arrivals

**Phase:** Stretch · **Estimate:** 4 h · **Depends on:** T13, T19

## Ask

Simulate a full shift in SimPy with dynamic order arrivals, comparing batching every N minutes with
batching every M orders.

## Why

Static benchmarks ignore when orders arrive. This answers the operational question of how often to
release batches, trading distance for lateness.

## How

- SimPy process for arrivals (from `order_arrivals`), a batching trigger policy, and pickers.
- Metrics: total distance, mean/max order lateness vs due date, picker utilisation.
- Sweep N and M; plot distance vs lateness.

## Plan

- [ ] Only start once T01–T28 are done
- [ ] Simulation model
- [ ] Policy sweep
- [ ] Chart and short write-up

## Acceptance criteria

- [ ] Simulation is deterministic per seed
- [ ] Both policy families compared on distance and lateness in one chart
- [ ] Findings summarised in `results/`
