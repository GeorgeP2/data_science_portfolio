# T09: Causal forest and DR-learner

**Phase:** 2 Heterogeneous effects · **Estimate:** 2 h · **Depends on:** T07

## Ask

Fit an EconML causal forest, plus a DR-learner as a robustness check.

## Why

Causal forests give honest CIs on CATE. The DR-learner checks that conclusions don't hinge on one
estimator.

## How

- `econml.dml.CausalForestDML` and `econml.dr.DRLearner`, with known propensities.
- Same grouped folds and features as T08.
- Feature importance for heterogeneity from the forest.

## Plan

- [ ] Causal forest
- [ ] DR-learner
- [ ] Heterogeneity feature importance
- [ ] Agreement table across all four learners

## Acceptance criteria

- [ ] Out-of-fold CATEs saved for both models
- [ ] Pairwise rank correlation of CATEs across the four learners reported
- [ ] Top drivers of heterogeneity listed from the causal forest
