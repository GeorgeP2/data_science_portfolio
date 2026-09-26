# T17: `make eval` and CI regression gate

**Phase:** 4 Evaluation · **Estimate:** 2 h · **Depends on:** T13, T15, T16

## Ask

Add `make eval` that prints accuracy / cost / latency tables, and run it in CI on the `ci` subset,
failing the build if accuracy regresses.

## Why

The first "done when" item. A regression gate turns the eval set into a guard against prompt and
model changes.

## How

- `make eval` runs the agent on a chosen subset, applies T15 + T16 scorers and prints tables by
  question type (accuracy, mean cost, p50/p95 latency).
- CI: runs the `ci` subset against the committed data sample, with cached LLM responses keyed on
  prompt + model so builds are cheap and deterministic. API key from a CI secret; skip cleanly when
  absent (e.g. on forks).
- Baseline scores committed; fail if accuracy drops by more than a configured threshold.

## Plan

- [ ] `make eval` target and table output
- [ ] Response cache
- [ ] Committed baseline + threshold
- [ ] CI job

## Acceptance criteria

- [ ] `make eval` prints accuracy, cost and latency tables by question type
- [ ] CI runs the `ci` subset and fails on a deliberate regression (demonstrated once)
- [ ] CI never needs the blob container; no API key is committed
