# T14: Feature-parity test in CI

**Phase:** 3 Streaming · **Estimate:** 1.5 h · **Depends on:** T07, T12

## Ask

Write a test proving the features the streaming scorer computes equal the offline features for the
same transactions.

## Why

"Feature-parity test in CI" is a "done when" item, and it's the guard against training/serving skew.

## How

- Committed synthetic fixture (a few hundred transactions across a handful of cards, with timestamp
  ties and window-edge cases). No raw TabFormer data in CI.
- Run the offline pipeline and the scorer's processing path (without the broker: feed messages
  through the same deserialise → state → featurise code) and compare feature vectors exactly
  (floats within a tight tolerance).
- Also run it for both state backends; Redis via a fake or skipped when unavailable, with the
  in-memory case always running.

## Plan

- [ ] Build the fixture
- [ ] Refactor the scorer so its per-message path is callable without Kafka
- [ ] Parity test
- [ ] Confirm it runs in `make check`

## Acceptance criteria

- [ ] Test passes in CI with no network or raw data
- [ ] Introducing a deliberate skew (e.g. including the current transaction in a window) makes it fail
- [ ] Fixture covers ties, window boundaries and a card's first transaction
