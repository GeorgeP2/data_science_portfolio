# T17: Time-to-decision across the ASOS experiments

**Phase:** 3 Sequential testing · **Estimate:** 2 h · **Depends on:** T15, T16

## Ask

Run fixed-horizon, mSPRT and O'Brien–Fleming on all ASOS experiments and report time-to-decision and
decision agreement. Produce the sequential-testing chart for the README.

## Why

This answers headline question 2: how much sooner could decisions be made, with false positives
controlled.

## How

- Per experiment and metric: checkpoint at which each method stops, and its decision.
- There's no ground truth for real effects, so report: time saved, agreement with the fixed-horizon
  decision, and false-positive control from T14/T15/T16 nulls. Say this plainly.
- CUPED can't be applied here (aggregate-only data; brief risk). Quantify its likely extra speed-up
  by applying T06's variance reduction as a hypothetical, clearly labelled.

## Plan

- [ ] Run all methods over all experiments
- [ ] Summary: median and distribution of time-to-decision per method
- [ ] Agreement matrix
- [ ] Sequential-testing chart to `reports/figures/`

## Acceptance criteria

- [ ] Every experiment × method has a stopping time and decision, or a stated reason for exclusion
- [ ] Chart shows time-to-decision distribution per method
- [ ] Any CUPED speed-up is labelled as a projection, not a measurement
- [ ] Chart regenerates from `make analysis`
