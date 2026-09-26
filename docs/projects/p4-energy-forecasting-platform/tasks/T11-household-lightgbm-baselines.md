# T11: Household LightGBM baselines

**Phase:** 3 Household model · **Estimate:** 2 h · **Depends on:** T05, T06, T08

## Ask

Fit per-household and pooled (one-size-fits-all) LightGBM models on LCL, with quantile outputs.

## Why

Headline question 2 compares the hierarchical model against these two. All three need the same
targets, splits and metrics.

## How

- Choose the household target and horizon (e.g. next-day half-hourly or daily kWh) and use it for all
  three household models.
- Compare on pre-2013 data so the ToU trial doesn't confound the comparison.
- Simulate sparse history by truncating training data (e.g. to 2, 4, 8 and 26 weeks per household).
- Per-household: one model each (on the development sample). Pooled: one model with household-level
  features.

## Plan

- [ ] Fix target, horizon and evaluation period
- [ ] History-truncation splits
- [ ] Per-household LightGBM
- [ ] Pooled LightGBM
- [ ] MAE and coverage by history length

## Acceptance criteria

- [ ] Both baselines are evaluated on the same households, splits and metrics
- [ ] Results are broken down by history length
- [ ] Target, horizon and period are documented in `config.yaml`
