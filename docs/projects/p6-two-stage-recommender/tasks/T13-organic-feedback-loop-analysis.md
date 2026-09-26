# T13: Organic vs recommended analysis and feedback-loop write-up

**Phase:** 4 Analysis · **Estimate:** 2.5 h · **Depends on:** T03, T12

## Ask

Compare organic and recommended listens, test what training on recommended listens does, and write
a short feedback-loop write-up.

## Why

Answers headline question 3 and is the third "Done when" item. It also covers the design decision on
exposure bias in offline evaluation.

## How

- Descriptive: popularity distribution, `played_ratio`, like rate and catalogue concentration of
  organic vs recommended events.
- Experiment: retrain one model (ALS, for speed) on organic-only vs all events; compare on organic
  and recommended test slices, coverage and popularity bias.
- Argument: models trained and evaluated on recommended events reward agreeing with the existing
  recommender, which narrows the catalogue over time.

## Plan

- [ ] Descriptive comparison with plots
- [ ] Organic-only vs all-events retrain
- [ ] Write-up (~1 page) in `results/`

## Acceptance criteria

- [ ] At least 3 organic vs recommended comparisons, each with a number and a plot
- [ ] Retrain comparison reported on both test slices plus coverage and popularity bias
- [ ] Write-up states conclusions and their limits (observational data, unknown logging policy)
