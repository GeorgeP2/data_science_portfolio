# T04: Low Carbon London download and Parquet conversion

**Phase:** 1 Data · **Estimate:** 2 h · **Depends on:** T01

## Ask

Download the LCL smart-meter data (~765 MB zip → ~11 GB CSV, ~167M rows), convert it once to
partitioned Parquet, and create a small household sample for development.

## Why

11 GB of CSV is too slow to iterate on. Project 5 also uses LCL (the ToU trial households), so the
loader belongs in `src/portfolio/` to avoid a second copy.

## How

- Scripted download with a pinned checksum into `data/raw/lcl/`.
- Stream the CSV in chunks (Polars `scan_csv` or pyarrow) into Parquet partitioned by tariff group
  and month; cast kWh to float and parse timestamps once.
- Sampled subset (e.g. 200 households, stratified by tariff group) in `data/processed/lcl_sample/`.
- Also capture the 2013 ToU price schedule shipped with the dataset (confirm where it lives).

## Plan

- [ ] Download script with checksum
- [ ] Chunked CSV → Parquet converter in `src/portfolio/`
- [ ] Stratified development sample
- [ ] Load the ToU price schedule
- [ ] `data/README.md` LCL section

## Acceptance criteria

- [ ] Conversion runs end to end without exceeding available memory
- [ ] Row count in Parquet equals the CSV row count (reported)
- [ ] Household count matches the documented 5,567 (or the difference is explained)
- [ ] Development sample loads in under 5 s
