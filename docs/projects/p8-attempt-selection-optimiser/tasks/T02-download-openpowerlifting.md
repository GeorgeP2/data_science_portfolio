# T02: Download script for the OpenPowerlifting bulk CSV

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Script the download of the OpenPowerlifting bulk zip into `data/raw/`, recording the snapshot date
and checksum.

## Why

Raw data is never committed. The bulk file is regenerated regularly, so results are only
reproducible if the exact snapshot is recorded.

## How

- Streaming download, unzip into `data/raw/openpowerlifting/`.
- Record the snapshot date and SHA-256 in `data/README.md`. The file changes upstream, so the
  checksum pins *the snapshot used*, not the URL.
- Convert the CSV to parquet in `data/processed/` with explicit dtypes for fast reloads.

## Plan

- [ ] Confirm the bulk URL and current download size
- [ ] Write the download script (or a `make data` target)
- [ ] Parquet conversion
- [ ] `data/README.md`: URL, public-domain licence, attribution line, snapshot date, checksum

## Acceptance criteria

- [ ] One command downloads and converts the data from a clean checkout
- [ ] Snapshot date and checksum are recorded, and a re-run detects a different snapshot
- [ ] `data/README.md` credits OpenPowerlifting
