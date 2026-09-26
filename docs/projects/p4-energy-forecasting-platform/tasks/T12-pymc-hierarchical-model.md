# T12: PyMC hierarchical household model

**Phase:** 3 Household model · **Estimate:** 4 h · **Depends on:** T05, T11

## Ask

Build a PyMC model with household → group → global partial pooling, and fit it with both NUTS and
variational inference.

## Why

It's the core of headline question 2. Sampling cost vs benefit, and the use of VI, is a design
decision to write up.

## How

- Likelihood on (log) consumption with daily/weekly profile and temperature effects. Household
  parameters are drawn from group-level priors, which are drawn from global priors. Non-centred
  parameterisation.
- Prior predictive check before fitting.
- Fit on the development sample with NUTS and check R-hat, ESS and divergences. Fit the same model
  with ADVI. Record wall time for both.
- Posterior predictive intervals for the same horizon and metrics as T11.

## Plan

- [ ] Write the model specification down first
- [ ] Prior predictive check
- [ ] NUTS fit + diagnostics
- [ ] ADVI fit
- [ ] Posterior predictive forecasts

## Acceptance criteria

- [ ] NUTS fit has R-hat < 1.01 and no divergences, or they're reported and addressed
- [ ] Wall time and sample size are recorded for NUTS and ADVI
- [ ] Forecasts use the same target, splits and metrics as T11
