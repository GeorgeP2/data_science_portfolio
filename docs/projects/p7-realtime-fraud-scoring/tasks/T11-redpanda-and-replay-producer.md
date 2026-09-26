# T11: Redpanda and replay producer

**Phase:** 3 Streaming · **Estimate:** 2 h · **Depends on:** T04

## Ask

Run Redpanda in Docker Compose and write a producer that replays TabFormer transactions in event-time
order, keyed by card, at a configurable speed-up.

## Why

The replay is what makes the streaming work genuine. Keying by card keeps each card's transactions in
order within a partition, which the per-card state relies on.

## How

- `docker-compose.yml` with a single-node Redpanda; topics `transactions` and `decisions` created on start.
- Producer reads `event_seq`-ordered parquet (default: test period), sleeps to match event-time gaps
  divided by the speed-up factor `N` (`N=0` means as fast as possible).
- Message key = card key; value = JSON (or a compact schema) with the fields the scorer needs plus
  `event_seq` and a produce timestamp for latency measurement.

## Plan

- [ ] Compose file with Redpanda
- [ ] Topic creation
- [ ] Producer with speed-up factor
- [ ] `make replay` target

## Acceptance criteria

- [ ] `make up` starts Redpanda and creates both topics
- [ ] `make replay` publishes the test period in `event_seq` order per card
- [ ] Consuming a partition shows each card's messages in increasing `event_seq`
- [ ] Achieved rate at a given `N` is logged
