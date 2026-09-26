# T08: T-learner and X-learner

**Phase:** 2 Heterogeneous effects · **Estimate:** 2 h · **Depends on:** T07

## Ask

Fit T-learner and X-learner CATE models for each mailing arm vs control.

## Why

They're the standard meta-learner baselines, and simple enough to explain in the memo.

## How

- Gradient-boosted base learners; out-of-fold CATE predictions via T07's grouped folds.
- One model per arm vs control. If time is short, use only the arm with the largest ATE and say so.
- The propensity is known from the design, so use it in the X-learner rather than estimating it.

## Plan

- [ ] T-learner
- [ ] X-learner
- [ ] Save out-of-fold predictions for T10
- [ ] Seeded tests on synthetic data with a known CATE

## Acceptance criteria

- [ ] Both recover a known heterogeneous effect on synthetic data (Spearman rank correlation > 0.5)
- [ ] Out-of-fold CATEs saved for every individual
- [ ] Mean predicted CATE lies within the T05 ATE CI for each arm
