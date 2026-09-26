# T16: Group-sequential design (O'Brien–Fleming)

**Phase:** 3 Sequential testing · **Estimate:** 2 h · **Depends on:** T14

## Ask

Implement a group-sequential test with O'Brien–Fleming boundaries (via an alpha-spending function)
on the ASOS checkpoints.

## Why

The classical alternative to always-valid methods: more power, less flexibility. It's one side of the
"power vs flexibility" design decision.

## How

- Lan–DeMets O'Brien–Fleming-type spending over information fractions derived from each
  experiment's sample sizes.
- Boundaries computed numerically (or with a library if one is available and trustworthy; state which).
- Planned maximum sample size = the experiment's final observed size.

## Plan

- [ ] Boundary computation
- [ ] Decision rule at each checkpoint
- [ ] Validate on T14 nulls
- [ ] Compare boundaries to published tables for equal-spaced looks

## Acceptance criteria

- [ ] Boundaries match published O'Brien–Fleming values for 5 equally spaced looks to 2 decimal places
- [ ] False-positive rate on T14 nulls is within Monte Carlo error of alpha
- [ ] Works with the irregular information fractions in the real data
