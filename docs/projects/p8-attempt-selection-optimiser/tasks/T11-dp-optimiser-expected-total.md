# T11: Dynamic-programming optimiser for expected total

**Phase:** 3 Optimiser · **Estimate:** 3 h · **Depends on:** T10

## Ask

Optimise the 9-attempt plan by dynamic programming to maximise expected total, enforcing 2.5 kg
increments and the "no lower weight after a successful attempt" rule.

## Why

This is the core decision engine, and expected total is the first objective in the brief.

## How

- State: best lift so far, attempt index, previous outcome (plus the last weight taken in the current lift).
- Action: next weight on a 2.5 kg grid, within a bounded range around the lifter's estimated max.
- Bombing out (no successful attempt in a lift) gives a total of 0; model it explicitly.
- Rules: 2.5 kg increments; the weight after a successful attempt must be higher. Confirm the rule
  after a missed attempt (whether the same weight may be repeated) from the federation rulebooks.
- Output is a policy (next weight for each state), not just one fixed plan.

## Plan

- [ ] State and action definitions
- [ ] Backward induction per lift, combined across lifts
- [ ] Rule enforcement in the action generator
- [ ] Tests against brute force on a coarse grid

## Acceptance criteria

- [ ] Matches brute-force enumeration on a small grid
- [ ] Never proposes an illegal weight (proved in T12)
- [ ] Solves a full 9-attempt plan in under 1 s, fast enough for the demo
