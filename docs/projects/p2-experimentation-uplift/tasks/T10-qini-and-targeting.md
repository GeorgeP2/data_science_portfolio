# T10: Qini curves and targeting at a fixed budget

**Phase:** 2 Heterogeneous effects · **Estimate:** 2.5 h · **Depends on:** T08, T09

## Ask

Produce Qini / uplift curves with bootstrap CIs for every learner, and quantify the extra outcomes
from uplift targeting vs random and "treat everyone" at a fixed mailing budget.

## Why

This answers headline question 1, produces the Qini chart for the README, and covers the "evaluating
uplift without per-individual ground truth" design decision.

## How

- Qini and uplift-at-k% on out-of-fold predictions; Qini coefficient per learner.
- Bootstrap by **household** for CIs.
- Budget as a parameter: extra votes per 1,000 mailings vs random, at several budget levels.
- Expect modest lift with ~8 features (brief risk). Report it honestly.

## Plan

- [ ] Qini / uplift curve functions, tested on a hand-computed case
- [ ] Household bootstrap CIs
- [ ] Budget table
- [ ] Qini chart to `reports/figures/`

## Acceptance criteria

- [ ] Qini function matches a hand-computed example
- [ ] Every learner has a curve with a CI band; the random baseline is shown
- [ ] Table of extra outcomes vs random and vs treat-everyone at ≥ 3 budget levels, with CIs
- [ ] Chart regenerates from `make analysis`
