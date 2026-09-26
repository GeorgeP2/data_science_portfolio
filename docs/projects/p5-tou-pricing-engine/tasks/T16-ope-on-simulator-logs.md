# T16: Apply OPE to the simulator's logs

**Phase:** 5 OPE · **Estimate:** 1.5 h · **Depends on:** T12, T14

## Ask

Use logs from one pricing policy in the simulator to estimate a new policy's margin off-policy. Then
run the new policy in the simulator and compare.

## Why

This answers headline question 2 for pricing. It also shows where OPE breaks (support mismatch, high
variance), which the write-up needs.

## How

- Logging policy: the T12 bandit, or an exploratory randomised tariff. Target: the optimiser's
  schedule, or a modified bandit.
- Compare the estimates with the simulator's on-policy truth.
- Deliberately include a target policy with poor support, to show OPE failing.

## Plan

- [ ] Generate logs with propensities
- [ ] Estimate the target policies
- [ ] On-policy ground-truth runs
- [ ] Short results note

## Acceptance criteria

- [ ] Estimated vs true margin reported per estimator for ≥ 2 target policies
- [ ] At least one case shows OPE failing, with the cause quantified (e.g. effective sample size)
