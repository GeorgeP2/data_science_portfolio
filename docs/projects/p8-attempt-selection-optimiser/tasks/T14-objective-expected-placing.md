# T14: Objective: expected placing against a simulated field

**Phase:** 3 Optimiser · **Estimate:** 2.5 h · **Depends on:** T11, T13

## Ask

Add an expected-placing objective, with the field simulated from the real entries of comparable meets.

## Why

Placing is where playing safe vs going for it matters most (headline question 3).

## How

- Field: sample competitors' totals from past entries matching sex × equipment × weight class ×
  federation. Aggregate data only; no names.
- Reward: expected place given the final total and the simulated field.
- Treat the field as independent of the lifter's choices, and state this simplification.

## Plan

- [ ] Field sampler
- [ ] Placing reward in the DP
- [ ] Monte Carlo check of the policy
- [ ] Worked example: a conservative third deadlift when chasing a placing

## Acceptance criteria

- [ ] DP expected place matches Monte Carlo within a stated tolerance
- [ ] Worked example shows when the placing objective picks a safer third attempt than expected total does
- [ ] Field sampler output contains no names
