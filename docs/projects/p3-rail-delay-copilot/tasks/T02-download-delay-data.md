# T02: Download delay attribution data and mirror a sample

**Phase:** 0 Setup · **Estimate:** 2 h · **Depends on:** T01

## Ask

Script the download of 2–3 years of Network Rail historic delay attribution periods and the
`Reference Files/` glossary into `data/raw/`, and commit a small OGL sample for CI and demos.

## Why

Blob URLs aren't a stable API. A scripted, checksummed download reproduces the full data; a committed
sample means CI and the demo never depend on the blob container.

## How

- List the `historic-delay-attribution` container, pick the period range from `config.yaml`, stream
  the zips, record SHA-256 checksums, skip files already present.
- Sample: a few thousand rows from one period, stratified by top reason codes, saved as a small
  CSV/parquet inside the project but outside `data/` (which is git-ignored).
- `data/README.md`: source, OGL attribution, period range, sizes.

## Plan

- [ ] Confirm the container URL and per-period file naming
- [ ] Download script with checksums
- [ ] Download the chosen periods
- [ ] Build and commit the sample with a note on how it was drawn
- [ ] Write `data/README.md`

## Acceptance criteria

- [ ] One command downloads the configured periods from a clean checkout; re-running is a no-op
- [ ] A truncated file fails the checksum check
- [ ] Committed sample is under ~5 MB and carries the OGL attribution
- [ ] Glossary / reference files are downloaded alongside
