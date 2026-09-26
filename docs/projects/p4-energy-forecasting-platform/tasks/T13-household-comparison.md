# T13: Household model comparison and verdict

**Phase:** 3 Household model · **Estimate:** 2 h · **Depends on:** T11, T12

## Ask

Produce the hierarchical vs LightGBM comparison table and the household calibration plot, and write
an honest verdict.

## Why

Both are "Done when" items. This is where the project answers when partial pooling helps and when it
doesn't.

## How

- Table: model × history length → MAE, 90% coverage, interval width, plus fit time.
- Break results down by group size to show where pooling helps (sparse groups).
- Household calibration plot to sit alongside the national one.
- The verdict states which model wins where, including if LightGBM wins.

## Plan

- [ ] Assemble results
- [ ] Table in `docs/projects/p4-energy-forecasting-platform/results/`
- [ ] Household calibration plot in `reports/figures/`
- [ ] Short verdict paragraph

## Acceptance criteria

- [ ] Table covers all three models at every history length
- [ ] Household calibration plot is saved
- [ ] Verdict is backed by the table and states the Bayesian model's cost (fit time)
