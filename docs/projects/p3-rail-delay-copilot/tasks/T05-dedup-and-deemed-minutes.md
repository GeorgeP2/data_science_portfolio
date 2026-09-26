# T05: Deduplicate incidents and separate deemed minutes

**Phase:** 1 Ingestion · **Estimate:** 2 h · **Depends on:** T04

## Ask

Build clean views: incidents deduplicated on `INCIDENT_NUMBER` + create date, and cancellation
"deemed minutes" kept separate from actual delay minutes.

## Why

Delay rows repeat per affected train, so naive counts inflate incidents. Mixing deemed minutes with
actual ones gives wrong "which causes cost the most" answers.

## How

- `incidents` view: one row per `INCIDENT_NUMBER` + create date, with reason, description, location
  and total minutes.
- `delays` view: event-level rows with deemed and actual minutes split. Confirm from the glossary how
  cancellations and deemed minutes are encoded (event type).
- Document both rules in the schema description (T06).

## Plan

- [ ] Confirm how deemed minutes are encoded
- [ ] Create views
- [ ] Reconciliation checks
- [ ] Tests

## Acceptance criteria

- [ ] Unique incidents per period are reported and checked against the brief's figure (~78k; confirm)
- [ ] Actual + deemed minutes reconcile to the raw total
- [ ] Tests on the sample cover duplicate rows and a cancellation
