# T18: Group metrics and group-aware thresholds

**Phase:** 4 Fairness companion · **Estimate:** 2 h · **Depends on:** T17

## Ask

Compare false-positive rate and recall by age group at the cost-optimal threshold, then try
group-aware thresholds and report the trade-offs.

## Why

Answers headline question 3, and "fairness companion section with the group metrics table" is a
"done when" item.

## How

- Age groups from the BAF age attribute (confirm its encoding, e.g. binned decades); report group sizes.
- Table per group: size, fraud rate, FPR, recall, expected cost, with bootstrap confidence intervals
  (small groups make point estimates noisy).
- Group-aware thresholds: e.g. equalise FPR across groups; report the change in total cost and recall.
- Write-up states the trade-offs plainly without moralising.

## Plan

- [ ] Group definitions and sizes
- [ ] Metrics table with CIs at the single threshold
- [ ] Group-aware threshold variant
- [ ] Short write-up in `results/`

## Acceptance criteria

- [ ] Group metrics table with confidence intervals is committed
- [ ] Total cost and recall for single vs group-aware thresholds are compared
- [ ] Write-up states what changes, what it costs and the limitations
