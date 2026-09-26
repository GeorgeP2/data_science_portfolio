# T07: Stateful per-card features (single implementation)

**Phase:** 1 Offline model · **Estimate:** 3 h · **Depends on:** T04

## Ask

Implement the stateful features as an incremental per-card state update that both the offline
pipeline and the streaming scorer call.

## Why

Training/serving skew is the classic bug here. One implementation used in both places makes the parity
test (T14) a check rather than a hope.

## How

- `CardState` plus `update_and_featurise(state, txn) -> features`. Features are computed from state
  *before* adding the current transaction, so a transaction never sees itself.
- Features: counts and amount sums over 1h/24h/7d, time since last transaction, new merchant for this
  card, new MCC for this card, amount z-score against the card's running mean/std.
- Windows via per-card deques of `(timestamp, amount)` with expiry; running stats via Welford.
- State must be serialisable (for Redis in T13).
- Offline: iterate each card's transactions in `event_seq` order. Measure throughput on the full dataset.

## Plan

- [ ] State and update function
- [ ] Serialisation round trip
- [ ] Offline batch runner writing features to parquet
- [ ] Hand-computed tests per feature, including window edges and timestamp ties

## Acceptance criteria

- [ ] Each feature matches a hand calculation on a small fixture
- [ ] A transaction's features never depend on itself or later transactions
- [ ] State serialises and deserialises to an equal object
- [ ] Full-dataset feature build time is documented
