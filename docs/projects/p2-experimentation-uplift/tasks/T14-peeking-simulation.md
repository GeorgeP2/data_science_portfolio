# T14: Peeking simulation on null comparisons

**Phase:** 3 Sequential testing · **Estimate:** 2 h · **Depends on:** T13

## Ask

Simulate "peeking" (a fixed-horizon t-test at every checkpoint) on A/A-like null comparisons and show
the inflated false-positive rate.

## Why

This motivates sequential methods with the dataset's own checkpoint cadence rather than an abstract
example.

## How

- The data is aggregate-only, so build nulls by simulation: generate both arms from the control's
  observed per-checkpoint mean/variance and sample sizes, so there's no true effect. Confirm whether
  any experiments contain genuine A/A arms that can be used directly.
- Stop at the first checkpoint with p < alpha; report the realised false-positive rate vs alpha.

## Plan

- [ ] Null generator from sufficient statistics
- [ ] Peeking rule and fixed-horizon rule
- [ ] Monte Carlo over experiments and seeds
- [ ] False-positive-rate chart vs number of looks

## Acceptance criteria

- [ ] Fixed-horizon test alone has a false-positive rate within Monte Carlo error of alpha
- [ ] Peeking false-positive rate reported with a CI, across the real checkpoint schedules
- [ ] Simulation is seeded and reproducible
