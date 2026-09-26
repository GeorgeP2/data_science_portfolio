# T07: Leakage-safe feature pipeline

**Phase:** 2 Heterogeneous effects · **Estimate:** 1.5 h · **Depends on:** T03

## Ask

Build the feature pipeline for the CATE models, computing household-level aggregates (e.g.
`p2004_mean`) inside cross-validation folds.

## Why

The brief flags this leakage risk. Aggregates computed on the full data leak information across folds
and inflate the uplift curves.

## How

- A scikit-learn transformer that fits aggregates on the training fold only.
- Folds grouped by `hh_id` (`GroupKFold`) so a household never spans train and test.
- Feature list in `config.yaml`.

## Plan

- [ ] Household-aggregate transformer
- [ ] Grouped fold splitter
- [ ] Test proving no leakage

## Acceptance criteria

- [ ] No household appears in both train and test in any fold (asserted)
- [ ] Leakage test passes: a held-out row's own outcome never enters its features
- [ ] Feature list is config-driven
