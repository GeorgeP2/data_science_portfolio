# T13: Objective: probability of hitting a target total

**Phase:** 3 Optimiser · **Estimate:** 1 h · **Depends on:** T11

## Ask

Add a P(total ≥ target) objective to the optimiser.

## Why

Hitting a qualifying total is a common goal. This objective produces different risk behaviour from
expected total, which feeds headline question 3.

## How

- Extend the state with the running total across lifts; the terminal reward is 1 if total ≥ target.

## Plan

- [ ] Extend the state and terminal reward
- [ ] Tests: a target far below the expected total gives a safe plan; one far above gives an aggressive plan

## Acceptance criteria

- [ ] P(total ≥ target) from the DP matches a Monte Carlo simulation of the policy within ±1 pp
- [ ] At least one documented example where the plan differs from the expected-total plan
