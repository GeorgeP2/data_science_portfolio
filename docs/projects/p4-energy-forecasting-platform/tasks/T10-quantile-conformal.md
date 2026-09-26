# T10: Quantile LightGBM with conformal calibration

**Phase:** 2 National model · **Estimate:** 2.5 h · **Depends on:** T09

## Ask

Add quantile LightGBM and a conformal calibration step so prediction intervals hit their nominal
coverage, and produce the national calibration plot.

## Why

Headline question 1 is about calibrated intervals; this rung answers it. It also feeds the
"calibration vs sharpness, and why pinball loss alone isn't enough" write-up.

## How

- One LightGBM model per quantile (e.g. 0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95); fix quantile crossing
  by sorting.
- Conformalised quantile regression (CQR) on a rolling calibration window.
- Calibration plot: nominal vs empirical coverage, before and after conformal, plus a sharpness
  (mean interval width) comparison. Save with `portfolio.plotting.save_fig`.

## Plan

- [ ] Quantile models
- [ ] Crossing fix
- [ ] CQR calibration
- [ ] Backtest raw vs calibrated
- [ ] Calibration plot into `reports/figures/`

## Acceptance criteria

- [ ] Calibrated 90% intervals cover 90% ± 2 pp in the backtest, or the shortfall is explained
- [ ] Raw vs calibrated coverage and width are both reported
- [ ] National calibration plot is saved and regenerates from one command
