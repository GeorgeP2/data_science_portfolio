# T13: Redis state backend

**Phase:** 3 Streaming · **Estimate:** 2 h · **Depends on:** T12

## Ask

Move per-card state from process memory to Redis behind a `StateStore` interface, and compare latency
and recovery behaviour.

## Why

Headline question 2 asks what real-time features cost in latency and infrastructure. In-memory vs
Redis is the concrete answer, and it drives the "where state lives" write-up.

## How

- `StateStore` protocol with `InMemoryStore` and `RedisStore`; backend chosen in `config.yaml`.
- Redis: one key per card holding serialised `CardState`; get → update → set, pipelined.
- Recovery: after a scorer restart, Redis-backed state continues; commit Kafka offsets after the state
  write so replays after a crash are at-least-once (document the double-count risk).

## Plan

- [ ] `StateStore` interface and both implementations
- [ ] Redis service in Compose
- [ ] Restart test: kill scorer mid-replay, restart, compare features
- [ ] Latency comparison in-memory vs Redis

## Acceptance criteria

- [ ] Both backends pass the same state tests
- [ ] After a restart, Redis-backed features match an uninterrupted run (except documented at-least-once duplicates)
- [ ] Per-stage latency for both backends is recorded in `results/`
