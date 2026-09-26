# T15: mSPRT and always-valid confidence sequences

**Phase:** 3 Sequential testing · **Estimate:** 3 h · **Depends on:** T14

## Ask

Implement the mixture sequential probability ratio test (mSPRT) and always-valid confidence
sequences on the difference in means, working from cumulative sufficient statistics.

## Why

These are valid under continuous peeking, which is the fix for the problem T14 demonstrates.

## How

- Normal-mixture mSPRT (Johari et al.) on the difference in means; mixing variance tau² as a
  parameter in `config.yaml`, with a sensible default justified by T18's effect-size distribution
  (or a placeholder until T18 lands).
- Confidence sequence from the same mixture.
- Pure functions of (n, mean, variance) per arm per checkpoint.

## Plan

- [ ] mSPRT statistic and decision rule
- [ ] Confidence sequence
- [ ] Validate on T14 nulls: false-positive rate ≤ alpha under peeking
- [ ] Unit tests on synthetic streams with known effects

## Acceptance criteria

- [ ] On T14's null simulations, false-positive rate ≤ alpha (within Monte Carlo error) with peeking at every checkpoint
- [ ] Confidence sequence covers the true effect at ≥ 1 − alpha on synthetic streams
- [ ] Detects a planted effect on synthetic data
