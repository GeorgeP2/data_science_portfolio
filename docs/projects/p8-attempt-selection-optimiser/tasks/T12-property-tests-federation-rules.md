# T12: Property-based tests for federation rules

**Phase:** 3 Optimiser · **Estimate:** 1.5 h · **Depends on:** T11

## Ask

Prove with Hypothesis that the optimiser always respects federation rules.

## Why

It's a "Done when" criterion. A rule violation would make a recommendation unusable at a real meet.

## How

- Generate random lifter profiles, objectives and outcome sequences; follow the policy through each.
- Properties: every weight is a multiple of 2.5 kg; after a make, the next weight is strictly higher;
  after a miss, the next weight obeys the rule confirmed in T11; exactly 3 attempts per lift count
  towards the total.

## Plan

- [ ] Hypothesis strategies for profiles and outcome sequences
- [ ] One test per rule
- [ ] Extend to every objective once T13 and T14 exist

## Acceptance criteria

- [ ] Each rule has a property test running ≥ 500 examples
- [ ] Tests run in `make check` in under 30 s
- [ ] Tests cover every objective
