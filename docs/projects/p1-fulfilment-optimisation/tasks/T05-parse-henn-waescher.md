# T05: Parser for Henn & Wäscher instances

**Phase:** 1 Core model · **Estimate:** 1 h · **Depends on:** T03, T04

## Ask

Load each of the 96 Henn & Wäscher instances into an `Instance`.

## Why

These are the external benchmark the headline table is scored on. A wrong parse makes every reported
gap meaningless.

## How

- Inspect the file format first; write a parser that maps it to `Layout` + `Order`s.
- Sanity-check against the published description: 10 aisles × 90 locations, 40–100 orders.

## Plan

- [ ] Inspect a few files by hand
- [ ] Write `load_henn_waescher(path) -> Instance`
- [ ] Test on one small instance with hand-checked counts
- [ ] Summary script: instances, orders, lines, capacity

## Acceptance criteria

- [ ] All 96 instances parse without error
- [ ] Order counts per instance fall in 40–100 and layout is 10 × 90
- [ ] Parser test runs without the raw data (uses a tiny fixture in `tests/`)
