# T06: Static-feature LightGBM baseline

**Phase:** 1 Offline model · **Estimate:** 2 h · **Depends on:** T05, T09

## Ask

Train LightGBM on static, per-transaction features only.

## Why

Headline question 2 asks what stateful features add. That needs a baseline that uses no per-card history.

## How

- Features: amount, `Use Chip`, MCC, merchant state/city (encoded), `Errors`, hour of day, day of week.
- Handle imbalance with class weights or `scale_pos_weight`; early stopping on validation PR-AUC.
- Log metrics via `portfolio.evaluation`.

## Plan

- [ ] Static feature function
- [ ] Training entrypoint with seed and config
- [ ] Evaluate on validation with the T09 metrics

## Acceptance criteria

- [ ] `PYTHONPATH=src python -m real_time_card_fraud_scoring.train --features static` trains and writes metrics
- [ ] Validation PR-AUC and recall at the fixed FPR are reported; accuracy is not
- [ ] Deterministic for a fixed seed
