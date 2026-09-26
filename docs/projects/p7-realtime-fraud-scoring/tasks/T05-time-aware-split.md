# T05: Time-aware train/validation/test split

**Phase:** 1 Offline model · **Estimate:** 1 h · **Depends on:** T04

## Ask

Split TabFormer by event time: train on the earliest period, validate on the next, test on the latest.

## Why

A random split leaks the future into training and inflates every metric. The replay also needs a test
period the model has never seen.

## How

- Cut-off dates in `config.yaml`, chosen so each split has enough fraud positives to evaluate.
- Stateful features for a validation/test transaction may use earlier history from any split (that's
  what production sees), but labels must not cross the cut-off.

## Plan

- [ ] Choose cut-offs from fraud counts per month
- [ ] Split function
- [ ] Tests: no overlap, ordered boundaries

## Acceptance criteria

- [ ] Splits are disjoint and time-ordered
- [ ] Size and fraud count of each split are reported
- [ ] The test period is the one used for replay and final numbers
