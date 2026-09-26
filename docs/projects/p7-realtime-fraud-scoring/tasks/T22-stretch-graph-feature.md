# T22 (stretch): Shared-merchant graph feature

**Phase:** Stretch · **Estimate:** 3 h · **Depends on:** T08, T14

## Ask

Add a graph feature: for each transaction, how many recently flagged cards have used the same merchant.

## Why

Fraud often clusters around compromised merchants. This tests whether a cross-card feature adds lift
and what it costs in state and latency.

## How

- Per-merchant state of recently flagged cards (time-windowed), updated when a decision is a decline
  (or when a label arrives, if T21 is done; state which, as it changes leakage).
- Add to the same shared feature code so the parity test covers it.
- Re-run the ablation and latency measurements.

## Plan

- [ ] Only start once T01–T20 are done
- [ ] Merchant state and feature
- [ ] Extend the parity test
- [ ] Ablation and latency comparison

## Acceptance criteria

- [ ] Parity test covers the new feature
- [ ] Lift and latency cost are reported next to the other feature groups
- [ ] Leakage reasoning is written down
