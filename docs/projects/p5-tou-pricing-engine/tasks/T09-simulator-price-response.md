# T09: Simulator: price response with known true elasticities

**Phase:** 2 Simulator · **Estimate:** 2 h · **Depends on:** T07, T08

## Ask

Add price response to the simulator, using "true" elasticities drawn from the T07 posterior.

## Why

Known true elasticities are what make regret measurable: the oracle knows them, the bandit has to
learn them.

## How

- When the simulator is created, draw one elasticity set per segment × time-of-day block from the
  posterior (seeded). This is the ground truth for that run.
- Demand at price p = baseline × response(p, elasticity), using the functional form from T07.
- Expose `true_elasticities` to the oracle only.
- Clip to plausible ranges and log whenever clipping happens.

## Plan

- [ ] Draw ground truth from the saved posterior
- [ ] Response function
- [ ] Oracle access to ground truth
- [ ] Tests: a higher price never raises demand within a segment; LCL High/Low response is reproduced at trial prices

## Acceptance criteria

- [ ] At the LCL trial prices, simulated response is within the T07 intervals
- [ ] Demand never increases with the price in the same period
- [ ] Different seeds give different ground truths; the same seed gives the same one
