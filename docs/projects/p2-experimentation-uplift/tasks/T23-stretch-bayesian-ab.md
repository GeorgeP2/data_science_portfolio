# T23 (stretch): Bayesian A/B analysis

**Phase:** Stretch · **Estimate:** 3 h · **Depends on:** T05

## Ask

Analyse the same GGL arms with a Bayesian model in PyMC and compare with the frequentist results.

## Why

Shows the same question answered in a second framework, and gives decision-friendly outputs such as
the probability that an arm beats control by more than a threshold.

## How

- Hierarchical logistic model with a household random effect (respecting clustering); weakly
  informative priors stated up front.
- Posterior of each arm's effect; P(effect > threshold); compare with T05 CIs.

## Plan

- [ ] Only start once T01–T22 are done
- [ ] Model and prior predictive check
- [ ] Fit and diagnostics (R-hat, ESS)
- [ ] Comparison table vs T05

## Acceptance criteria

- [ ] Diagnostics pass (R-hat < 1.01, no divergences)
- [ ] Posterior means within the frequentist CIs, or the difference is explained
- [ ] Short write-up in `results/`
