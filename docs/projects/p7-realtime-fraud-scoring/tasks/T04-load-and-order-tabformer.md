# T04: Load, clean and order TabFormer

**Phase:** 1 Offline model · **Estimate:** 2 h · **Depends on:** T02

## Ask

Load the raw TabFormer CSV into typed parquet with an event timestamp, a card key and a deterministic
total ordering.

## Why

Timestamps are minute-level, so many transactions tie. Offline features, the replay producer and the
parity test all depend on agreeing on one order.

## How

- Parse the date/time columns into one event timestamp; parse amount (strip the currency symbol);
  `Is Fraud` to bool; card key = `(User, Card)`.
- Deterministic order: `(timestamp, card key, original row index)`, stored as an `event_seq` column
  that every downstream step sorts by.
- Chunked reading (polars or pandas); write `data/processed/transactions.parquet`.
- Quick profile: row count (brief says ~24M; confirm), fraud rate, rows per card, share of timestamp ties.

## Plan

- [ ] Inspect the raw columns
- [ ] Loader with a typed schema
- [ ] `event_seq` ordering
- [ ] Profiling notebook calling into `src/`
- [ ] Tests on a small fixture

## Acceptance criteria

- [ ] Parquet has one row per raw transaction, typed columns and `event_seq`
- [ ] `event_seq` is unique and identical across runs
- [ ] Profile reports row count, fraud rate and share of timestamp ties
- [ ] Fixture test runs without raw data
