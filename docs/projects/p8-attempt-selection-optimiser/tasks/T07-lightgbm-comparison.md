# T07: LightGBM comparison

**Phase:** 2 Make-probability model · **Estimate:** 1 h · **Depends on:** T06

## Ask

Fit LightGBM on the full feature set as a flexible comparison model.

## Why

Shows how much a black-box model gains over the baseline, and supplies the evidence for the
"latent strength vs direct classifier" write-up on extrapolation.

## How

- Same features and split; early stopping on a time-based validation slice of the training set.
- Check extrapolation: predictions for jumps larger than typical (e.g. the top 1% of jump %).

## Plan

- [ ] Fit with a time-based validation slice
- [ ] Evaluate with the T06 harness
- [ ] Probability vs jump % curve, including large jumps

## Acceptance criteria

- [ ] Metrics reported alongside the baseline
- [ ] Probability-vs-jump curve saved for the write-up
