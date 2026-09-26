# T24 (stretch): Hierarchical reconciliation check

**Phase:** Stretch · **Estimate:** 2 h · **Depends on:** T12

## Ask

Check that household forecasts sum sensibly to group totals.

## Why

Forecasts at different levels of a hierarchy should be coherent. Checking it shows whether the
hierarchical model is internally consistent.

## How

- Compare the sum of household forecasts to a direct group-level forecast and to actual group totals.
- Report the incoherence gap; optionally apply a simple reconciliation (e.g. bottom-up or MinT) and
  compare accuracy before and after.

## Plan

- [ ] Only start once T01–T22 are done
- [ ] Group-level aggregation
- [ ] Coherence metric
- [ ] Optional reconciliation

## Acceptance criteria

- [ ] Coherence gap is reported per group
- [ ] If reconciliation is applied, accuracy before and after is compared
- [ ] Findings summarised in `results/`
