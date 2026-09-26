# T13: Load and validate the ASOS experiments

**Phase:** 3 Sequential testing · **Estimate:** 1 h · **Depends on:** T02

## Ask

Load the ASOS Digital Experiments Dataset into a tidy table of per-arm cumulative sufficient
statistics per checkpoint, and validate it.

## Why

All of Part B reads this table. The data is aggregate-only, so the structure must be understood
before any method is built on it.

## How

- Confirm the schema from the paper/OSF page: experiment id, variant, metric, checkpoint time,
  count, mean, variance. Confirm the counts (78 experiments, ~24k rows) and checkpoint granularity.
- Checks: counts non-decreasing over checkpoints, variances non-negative, one control per experiment.

## Plan

- [ ] Inspect the parquet and documentation
- [ ] Write `load_asos() -> DataFrame`
- [ ] Validation checks and a summary table (experiments, metrics, checkpoints, arms)
- [ ] Fixture test

## Acceptance criteria

- [ ] Loader returns one row per experiment × metric × arm × checkpoint
- [ ] Validation checks pass, or failing experiments are listed and excluded with the reason
- [ ] Summary table of experiment counts and durations saved
- [ ] Fixture test runs without raw data
