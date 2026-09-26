# T02: Download script for the KIT benchmark suite

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Write a script that downloads the KIT Manual Warehouse Order Picking benchmarks (~2 GB JSON) into
`data/raw/kit/` and verifies them against pinned checksums.

## Why

The generator is calibrated on this suite. Raw data is never committed, so the only route to
reproducing the calibration is a scripted, checksummed download.

## How

- Plain `requests`/`urllib` streaming download from the RADAR dataset page; resumable if cheap.
- SHA-256 per file, pinned in the script or a `checksums.txt`.
- Idempotent: skips files that already exist with the right checksum.
- `data/README.md` records source, citation (Barlang, Lehmann, Furmans, 2026), CC BY 4.0 and attribution.

## Plan

- [ ] Find the stable download URL(s) on RADAR
- [ ] Write `scripts/download_kit.py` (or a `make data` target)
- [ ] Download once, record checksums, pin them
- [ ] Write the KIT section of `data/README.md`

## Acceptance criteria

- [ ] One command downloads the suite into `data/raw/kit/` from a clean checkout
- [ ] A corrupted or truncated file fails the checksum check with a clear error
- [ ] Re-running is a no-op when files are already present
- [ ] `data/README.md` has URL, licence, citation and size
