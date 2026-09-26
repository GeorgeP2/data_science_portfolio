# T21 (stretch): Delayed-label simulation

**Phase:** Stretch · **Estimate:** 3 h · **Depends on:** T12, T15

## Ask

Simulate fraud labels arriving days after the transaction and show the effect on monitoring.

## Why

In production, fraud labels (chargebacks) arrive late. Monitoring that assumes instant labels overstates
what you can know in real time.

## How

- A label topic fed with each fraud label delayed by a sampled lag (distribution and parameters in
  `config.yaml`, stated as assumptions).
- Monitor shows precision/recall computed on labels available so far vs the eventual truth.

## Plan

- [ ] Only start once T01–T20 are done
- [ ] Delayed label producer
- [ ] Monitoring metrics on available labels
- [ ] Chart: observed vs true recall over time

## Acceptance criteria

- [ ] Deterministic per seed
- [ ] Chart shows the gap between observed and true metrics over the replay
- [ ] Findings summarised in `results/`
