# T08: Hierarchical meet-day max model: specification

**Phase:** 2 Make-probability model · **Estimate:** 3 h · **Depends on:** T05

## Ask

Specify the PyMC model and validate it on a subsample. Each lifter has a latent meet-day max drawn
from a progression model on their history. An attempt succeeds if its weight is below that max,
adjusted for fatigue from earlier attempts. Lifters are pooled within sex × equipment × weight class.

## Why

This is the main model. Its structure gives sensible behaviour for big jumps and for lifters with only
one or two meets, which a direct classifier can't guarantee.

## How

- Meet-day max = f(previous bests, time since last meet) + group effect + noise.
- P(make) = P(max × fatigue(attempt index, earlier attempts) ≥ weight). Use a smooth link (e.g. probit
  on the margin) rather than a hard threshold so the posterior is well-behaved.
- Hierarchical priors across sex × equipment × weight class.
- Prior predictive checks: plausible make rates by attempt and jump size.
- Fit with NUTS on a subsample of a few thousand lifters before scaling.

## Plan

- [ ] Write the model maths in a docstring
- [ ] Implement in PyMC
- [ ] Prior predictive checks
- [ ] Fit on a subsample; check R-hat, ESS and divergences
- [ ] Posterior predictive checks by attempt number

## Acceptance criteria

- [ ] Prior predictive make rates fall in a documented plausible range
- [ ] Subsample fit has R-hat < 1.01 and no divergences
- [ ] Posterior predictive make rate by attempt matches the observed rate within stated intervals
