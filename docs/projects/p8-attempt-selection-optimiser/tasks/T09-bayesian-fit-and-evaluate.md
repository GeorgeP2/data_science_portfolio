# T09: Fit the Bayesian model at scale and evaluate

**Phase:** 2 Make-probability model · **Estimate:** 3 h · **Depends on:** T06, T08

## Ask

Fit the hierarchical model on the training set and compare it with the baseline and LightGBM on
held-out future meets.

## Why

Answers headline question 1: how well make probability can be predicted, and whether it's calibrated
on future meets.

## How

- NUTS on the full data may be too slow. Choose between a stratified subsample, variational inference
  (ADVI) or a faster backend (nutpie/numpyro), and record the choice and fit time.
- New lifters in the test set get predictions from the group-level posterior.
- Evaluate with the T06 harness, overall and for first-time lifters.

## Plan

- [ ] Choose and justify the inference approach
- [ ] Fit and save the posterior to `outputs/`
- [ ] Predictions on the test set
- [ ] Comparison table: baseline, LightGBM, Bayesian
- [ ] Calibration plot for the README

## Acceptance criteria

- [ ] Comparison table of log loss and Brier score, overall and for first-timers, for all three models
- [ ] Calibration plot on held-out future meets saved to `reports/figures/`
- [ ] Inference choice, fit time and diagnostics documented
