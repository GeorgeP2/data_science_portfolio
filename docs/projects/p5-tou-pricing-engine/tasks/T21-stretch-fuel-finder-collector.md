# T21 (stretch): Fuel Finder snapshot collector

**Phase:** Stretch · **Estimate:** 2 h · **Depends on:** T01

## Ask

Set up a scheduled job that snapshots UK Fuel Finder station prices, so a history exists if the
competitor-response extension (T22) goes ahead.

## Why

Fuel Finder has no official archive. The brief says to start collecting early; this is the only
stretch task whose value depends on *when* it starts.

## How

- Register via GOV.UK One Login and use the OAuth API. Confirm the endpoints, rate limits and
  fair-use policy first.
- A scheduled job (e.g. a cron on a cheap host or a scheduled CI workflow) polls at a fair-use-compliant
  interval and stores only changed prices, with timestamps.
- Keep credentials out of the repo. Store snapshots outside git.
- OGL v3: record attribution in `data/README.md`.

## Plan

- [ ] Decide now whether to pursue T22; if not, skip this task
- [ ] API access and credentials
- [ ] Collector job with change detection
- [ ] Monitoring: alert if snapshots stop

## Acceptance criteria

- [ ] Collector has run unattended for ≥ 7 days with no gaps longer than two polling intervals
- [ ] Polling respects the documented fair-use limits
- [ ] No credentials or snapshots are committed
