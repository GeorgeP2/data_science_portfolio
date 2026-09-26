# T09: Evaluation metrics and cost model

**Phase:** 2 Evaluation · **Estimate:** 1.5 h · **Depends on:** T01

## Ask

Implement PR-AUC, recall at a fixed false-positive rate, and an expected-cost function: a missed
fraud costs its amount; a false decline costs a margin plus a churn penalty.

## Why

AUC isn't the business metric. The cost model turns scores into money, which headline question 1 needs.

## How

- PR-AUC and recall@FPR go in `portfolio.evaluation` only if another project will use them; otherwise
  keep them local.
- `expected_cost(y, score, amount, threshold, costs)`; margin rate and churn penalty in `config.yaml`,
  each with its source or reasoning.

## Plan

- [ ] Metric functions
- [ ] Cost function and config
- [ ] Tests with hand-computed cases

## Acceptance criteria

- [ ] Tests cover all-fraud, no-fraud and mixed cases
- [ ] Cost parameters are in `config.yaml` with a stated rationale
- [ ] No accuracy metric is reported anywhere
