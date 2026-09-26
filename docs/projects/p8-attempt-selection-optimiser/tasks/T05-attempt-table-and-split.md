# T05: Attempt-level table, features and time split

**Phase:** 1 Data preparation · **Estimate:** 2 h · **Depends on:** T04

## Ask

Reshape to one row per attempt with features (jump %, attempt number, previous outcome, lifter
history) and split train/test by meet date.

## Why

Every model trains on this table. A time-based split is what makes "calibrated on future meets" a
meaningful claim.

## How

- Columns: lifter, meet, date, lift, attempt index, weight, made (from the sign), jump in kg and % vs
  the previous attempt, previous outcome, bodyweight, sex, equipment, weight class, age.
- History features from *prior meets only*: previous best per lift, number of meets, days since last meet.
- Split: cut-off date in `config.yaml`; flag first-time lifters in the test set.
- Name disambiguation is imperfect, so treat lifter histories as noisy.

## Plan

- [ ] Wide→long reshape
- [ ] Within-meet features
- [ ] History features without leakage
- [ ] Time split and first-timer flag
- [ ] Leakage test

## Acceptance criteria

- [ ] A test asserts no history feature uses a meet on or after the attempt's date
- [ ] Every test-set meet date is after every train-set meet date
- [ ] Table summary (rows, lifters, meets, make rate by attempt) is saved
