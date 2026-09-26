# T10: Cost curves, threshold choice and sensitivity

**Phase:** 2 Evaluation · **Estimate:** 2 h · **Depends on:** T08, T09

## Ask

Plot expected cost against threshold, choose the cost-minimising threshold on validation, and test how
sensitive it is to the cost assumptions.

## Why

This answers headline question 1, and "cost curve + chosen threshold in the README" is a "done when" item.

## How

- Cost curve on validation; take the minimum; report fraud loss prevented net of false-decline cost on test.
- Sensitivity: vary margin and churn penalty over a grid; show how the optimal threshold and net
  saving move.
- Figures via `portfolio.plotting.save_fig` into `reports/figures/`.

## Plan

- [ ] Cost curves for static and full models
- [ ] Threshold selection
- [ ] Sensitivity grid and chart
- [ ] Net saving on test

## Acceptance criteria

- [ ] Cost-curve figure with the chosen threshold marked
- [ ] Threshold is chosen on validation and reported on test
- [ ] Sensitivity chart shows threshold and net saving across the cost grid
- [ ] Threshold is saved alongside the model artefact for the scorer to use
