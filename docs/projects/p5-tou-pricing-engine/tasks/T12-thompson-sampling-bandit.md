# T12: Thompson-sampling pricing bandit

**Phase:** 4 Bandit · **Estimate:** 2.5 h · **Depends on:** T09

## Ask

Implement Thompson sampling over price levels per segment, learning online in the simulator. Log
every decision with its propensity.

## Why

Headline question 1 asks how close a bandit that has to *learn* the price response gets to the
optimum. The logged propensities are what make off-policy evaluation possible later (T16).

## How

- Arms: price levels from the optimiser's grid, per segment × time-of-day block.
- Reward: margin per decision. Keep a posterior per arm (e.g. Gaussian with known noise). Use a
  weakened version of the T07 posterior as the prior, so the bandit doesn't start with the truth.
- Enforce the price cap and step limits on sampled actions.
- Propensities: estimate by Monte Carlo sampling from the posterior at decision time. Log context,
  action, propensity and reward.

## Plan

- [ ] Arm and posterior design
- [ ] Constrained action sampling
- [ ] Propensity estimation and logging
- [ ] Seeded tests

## Acceptance criteria

- [ ] Deterministic per seed
- [ ] No logged action breaks the price cap or step limit
- [ ] Logged propensities are in (0, 1] and sum to ~1 across arms per decision
