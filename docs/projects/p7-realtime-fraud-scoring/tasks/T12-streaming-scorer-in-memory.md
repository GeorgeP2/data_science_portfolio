# T12: Streaming scorer with in-memory state

**Phase:** 3 Streaming · **Estimate:** 3 h · **Depends on:** T07, T10, T11

## Ask

Build the scorer: consume transactions, update per-card state in memory using the T07 function,
score with the saved model, apply the saved threshold and publish a decision.

## Why

This is the core of the service and the thing the latency SLO applies to.

## How

- Consumer group on `transactions`; state dict keyed by card; `update_and_featurise` from T07;
  LightGBM predict on a single row (or micro-batch; measure both).
- Warm-up: pre-load state from history before the test period so features match offline.
- Decision message: card, `event_seq`, score, decision, feature snapshot hash, per-stage timings
  (deserialise, feature, inference, publish).
- Handle out-of-order or duplicate events explicitly (drop, or process with a logged warning; choose and document).
- Scorer runs as a Compose service.

## Plan

- [ ] Consumer/producer loop
- [ ] State warm-up
- [ ] Scoring and decision publishing
- [ ] Per-stage timing
- [ ] Out-of-order handling
- [ ] Integration test against a local Redpanda (or a fake consumer)

## Acceptance criteria

- [ ] Every replayed transaction produces exactly one decision
- [ ] Decisions include per-stage timings
- [ ] Out-of-order behaviour is documented and tested
- [ ] Scorer restarts cleanly (in-memory state loss is documented, fixed in T13)
