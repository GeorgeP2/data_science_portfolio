# T05: Evaluation module

**Phase:** 1 Data · **Estimate:** 2 h · **Depends on:** T04

## Ask

Implement recall@k and NDCG@k overall and by slice (cold-start items, organic vs recommended events),
plus catalogue coverage and popularity bias.

## Why

Every model is scored by this one module, so comparisons in the metrics table are like for like.

## How

- Input: per-user ranked lists + test positives. Output: metrics per slice, written with
  `portfolio.evaluation`.
- Slices filter the *ground truth* (e.g. recall on cold-start positives only).
- Popularity bias: mean train-popularity percentile of recommended items vs of test positives.
  Coverage: share of the catalogue recommended to at least one user.
- Vectorised with Polars/NumPy; k values in `config.yaml`.

## Plan

- [ ] Metric functions
- [ ] Slice handling
- [ ] Coverage and popularity bias
- [ ] Unit tests on hand-computed toy cases

## Acceptance criteria

- [ ] recall@k and NDCG@k match hand calculations on at least 3 toy cases
- [ ] A perfect ranking scores 1.0 and an empty one 0.0
- [ ] Returns metrics for cold-start, organic and recommended slices separately
- [ ] Scores the full 50M test set in minutes, not hours
