# T04: Load periods into DuckDB

**Phase:** 1 Ingestion · **Estimate:** 2 h · **Depends on:** T02

## Ask

Load the downloaded periods into a DuckDB database with typed columns and a period identifier.

## Why

DuckDB backs the text-to-SQL tool and the classification dataset.

## How

- `read_csv` over the extracted files with an explicit schema (~40 columns); add `period` from the
  filename. Parse dates and cast `PFPI_MINUTES` to numeric.
- Load the glossary as lookup tables (reason codes, TOCs, responsible managers).
- Handle column drift across years (renames, extra columns) with a mapping in code, and log it.

## Plan

- [ ] Inspect column sets across the chosen periods
- [ ] Column mapping + explicit types
- [ ] Load script writing `data/processed/delays.duckdb`
- [ ] Lookup tables from the glossary
- [ ] Test on the committed sample

## Acceptance criteria

- [ ] Load runs end to end on the full range and on the sample
- [ ] Row count per period is reported and checked against the brief's figure (~580k per period; confirm)
- [ ] Any column drift between years is handled and documented
- [ ] Test runs in CI against the sample
