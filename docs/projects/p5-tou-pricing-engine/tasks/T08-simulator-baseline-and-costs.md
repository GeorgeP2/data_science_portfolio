# T08: Simulator: baseline demand and wholesale costs

**Phase:** 2 Simulator · **Estimate:** 2 h · **Depends on:** T02, T03

## Ask

Build the parts of the simulator that don't depend on price: weather-driven baseline household demand
per segment, and a half-hourly wholesale cost series derived from Agile.

## Why

Margin = (price − cost) × demand. Both baseline demand and cost must be realistic, or the optimiser
and bandit are solving a toy problem.

## How

- Baseline demand: fit per segment from LCL Std households (time of day, day type, temperature),
  then drive it with weather.
- Cost: derive a wholesale cost proxy from Agile. Confirm Octopus's published Agile formula before
  inverting it, and document the transformation.
- LCL covers 2011–2014 and Agile starts in 2018. State how the two are combined (e.g. LCL demand
  shapes with Agile-era cost paths).
- Simulator API: `step(prices, t) -> demand, cost` over a day of 48 half-hours; seeded.

## Plan

- [ ] Baseline demand model per segment
- [ ] Agile → cost transformation
- [ ] Simulator skeleton with seeded noise
- [ ] Tests: determinism, shapes, non-negative demand

## Acceptance criteria

- [ ] Simulated baseline reproduces LCL Std daily load shapes per segment (plot + error metric)
- [ ] Cost transformation is documented with its source
- [ ] Same seed gives identical output
