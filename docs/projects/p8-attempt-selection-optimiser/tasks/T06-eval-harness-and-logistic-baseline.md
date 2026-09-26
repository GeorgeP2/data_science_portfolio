# T06: Evaluation harness and logistic regression baseline

**Phase:** 2 Make-probability model · **Estimate:** 2 h · **Depends on:** T05

## Ask

Build a shared evaluation (log loss, Brier score, calibration plot; overall and for first-time lifters)
and fit the logistic regression baseline on jump %, attempt number and previous outcome.

## Why

Every model is compared with the same metrics on the same held-out meets. The baseline sets the bar
the Bayesian model has to beat.

## How

- `evaluate(y, p, groups)` returns metrics per group and writes them via `portfolio.evaluation`.
- Calibration: reliability diagram with bin counts, plus expected calibration error.
- Baseline in scikit-learn, including an attempt number × previous outcome interaction.

## Plan

- [ ] Evaluation function and calibration plot helper
- [ ] Logistic baseline
- [ ] Metrics for overall and first-timer slices

## Acceptance criteria

- [ ] Evaluation is unit-tested (perfect and constant predictors give known values)
- [ ] Baseline test-set metrics are in `outputs/metrics.json`
- [ ] Calibration plot saved to `reports/figures/`
