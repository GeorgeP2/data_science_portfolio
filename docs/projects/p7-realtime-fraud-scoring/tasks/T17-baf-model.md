# T17: BAF companion model

**Phase:** 4 Fairness companion · **Estimate:** 1.5 h · **Depends on:** T03, T09

## Ask

Train LightGBM on BAF months 0–5 and evaluate on months 6–7.

## Why

The fairness analysis needs a realistic model trained with the same time-aware discipline as the main project.

## How

- Use the variant chosen in T03. Split on `month`.
- Same metrics as T09. BAF is account applications, not card payments, so there is no transaction
  amount: define the cost model for this setting (e.g. fixed cost per missed fraud and per false
  positive) in `config.yaml` and state it plainly.
- Choose the cost-optimal threshold on a validation slice of months 0–5 (e.g. month 5).

## Plan

- [ ] Load and split
- [ ] Define BAF cost parameters
- [ ] Train and evaluate
- [ ] Cost-optimal threshold

## Acceptance criteria

- [ ] Months 0–5 train/validate, months 6–7 test, with no leakage
- [ ] PR-AUC, recall at fixed FPR and expected cost reported on test
- [ ] BAF cost assumptions are written down and differ from the TabFormer ones for a stated reason
