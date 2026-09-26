# T10: Make-probability interface

**Phase:** 2 Make-probability model · **Estimate:** 1 h · **Depends on:** T09

## Ask

Expose one function that returns P(make) for a proposed attempt, given a lifter profile and the meet
so far, backed by the fitted model.

## Why

The optimiser, retrospective analysis and demo all need the same probabilities. One interface keeps
them consistent and lets any of the three models be swapped in.

## How

- `p_make(profile, lift, attempt_index, weight, meet_so_far) -> float`.
- The profile holds only what a user could type: recent bests, bodyweight, sex, equipment, age.
- Load posterior summaries from a small artefact so the demo doesn't need the full trace.

## Plan

- [ ] Define the profile type and function signature
- [ ] Bayesian implementation from a compact artefact
- [ ] Baseline implementation behind the same interface
- [ ] Tests

## Acceptance criteria

- [ ] P(make) is in [0, 1] and non-increasing in weight (property test)
- [ ] Artefact is small enough to ship with the demo (size stated)
- [ ] Both implementations pass the same tests
