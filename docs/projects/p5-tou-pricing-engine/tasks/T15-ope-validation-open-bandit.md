# T15: Validate OPE on Open Bandit

**Phase:** 5 OPE · **Estimate:** 2 h · **Depends on:** T04, T14

## Ask

Estimate each logging policy's click rate from the other policy's logs, and compare the estimate with
that policy's actual on-policy click rate.

## Why

This is the "OPE validation table" in "done when". It's the only place the estimators are checked
against real ground truth.

## How

- Follow the Open Bandit paper's protocol (confirm the details). For example, estimate Bernoulli TS's
  value from the random policy's logs and compare it with Bernoulli TS's observed click rate.
- Do this per campaign, and in both directions where the propensities allow.
- Report relative error and CI coverage per estimator.
- State plainly that the reward is clicks, not revenue: this validates the estimators, not the pricing.

## Plan

- [ ] Target-policy action probabilities for each direction
- [ ] Run IPS, SNIPS and DR
- [ ] Write the table to `docs/projects/p5-tou-pricing-engine/results/`

## Acceptance criteria

- [ ] Table shows estimated vs actual value, relative error and CI per estimator × campaign
- [ ] Table regenerates from one command
- [ ] The clicks-not-revenue caveat sits next to the table
