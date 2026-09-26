# T02: NESO historic demand ingestion

**Phase:** 1 Data · **Estimate:** 2 h · **Depends on:** T01

## Ask

Download NESO historic demand (2001–present) into Parquet, with incremental updates for new data.

## Why

The national model retrains daily on fresh data, so ingestion has to be repeatable and incremental,
not a one-off download.

## How

- Backfill from the per-year CSVs; pick up recent periods via the CKAN API (no key). Confirm the
  current resource IDs and column names; they have changed between years.
- Store in `data/raw/neso/` as downloaded and `data/processed/neso/` as Parquet partitioned by year.
- Incremental mode: fetch only periods after the latest stored timestamp; idempotent on re-run.
- Choose the target (ND vs TSD) and write down why. Keep the embedded wind/solar columns, noting that
  they are modelled, not metered.

## Plan

- [ ] Confirm CSV and CKAN endpoints and column names per year
- [ ] Backfill function
- [ ] Incremental update function
- [ ] Record target choice (ND/TSD) in `config.yaml` with a comment
- [ ] `data/README.md` NESO section: source, licence, attribution

## Acceptance criteria

- [ ] One command backfills 2001–present into partitioned Parquet
- [ ] Re-running the incremental update adds only new periods (no duplicates on `(date, period)`)
- [ ] Column names are harmonised across years
- [ ] `data/README.md` documents the source, licence and that embedded generation is modelled
