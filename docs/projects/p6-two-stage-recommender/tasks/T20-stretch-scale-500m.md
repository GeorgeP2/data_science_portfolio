# T20 (stretch): Scale to the 500M version

**Phase:** Stretch · **Estimate:** 4 h · **Depends on:** T12

## Ask

Re-run the pipeline on the 500M-event version using Polars/DuckDB, and report how metrics and run
times change.

## Why

Shows the pipeline scales beyond a development sample, and whether conclusions hold with 10× data.

## How

- Switch data size in `config.yaml` (T02). Move the heaviest joins/aggregations to DuckDB or Polars
  streaming where memory requires it.
- Sample users for the two-tower training if needed; state the sample.

## Plan

- [ ] Only start once T01–T19 are done
- [ ] Download 500M and profile memory hotspots
- [ ] Port hotspots to streaming/DuckDB
- [ ] Re-run and compare

## Acceptance criteria

- [ ] Full pipeline runs on 500M on the available machine, with peak memory reported
- [ ] Metrics table for 500M sits next to the 50M one
- [ ] Changes in conclusions (if any) are stated
