# T07: Estimate price elasticities

**Phase:** 1 Elasticity · **Estimate:** 3 h · **Depends on:** T06

## Ask

Estimate how demand responds to High / Low price signals by time of day and household group, with
uncertainty.

## Why

These elasticities calibrate the simulator's "true" demand response. Without uncertainty the
simulator can't draw plausible alternatives, and the bandit has nothing realistic to learn.

## How

- If Project 4's PyMC work is done: hierarchical Bayesian model (household → group → global) of
  log-demand change vs price level, by time-of-day block. Otherwise: regression with group ×
  time-of-day interactions and bootstrap intervals (the brief's fallback).
- Control for temperature and calendar; compare to the Std group.
- Report elasticities as causal or associational per T05.

## Plan

- [ ] Choose model based on Project 4 status
- [ ] Fit on a sample, then full data
- [ ] Posterior/interval summaries by group × time of day
- [ ] Posterior predictive or held-out check
- [ ] Save posterior draws (or bootstrap samples) for T09

## Acceptance criteria

- [ ] Elasticity estimates with 90% intervals for every group × time-of-day block
- [ ] Held-out households or weeks are predicted better than a no-response baseline
- [ ] Draws are saved in a format the simulator loads
- [ ] Wording matches the T05 decision
