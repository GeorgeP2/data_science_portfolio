# T02: Download scripts for GGL and ASOS

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Script the download of the GGL 2008 social pressure data (Yale ISPS Dataverse) and the ASOS Digital
Experiments Dataset (OSF) into `data/raw/`, with pinned checksums. Optionally fetch Lenta via
`scikit-uplift` behind a flag.

## Why

Raw data is never committed. A scripted, checksummed download is the first step of `make analysis`.

## How

- Streaming download, SHA-256 check, idempotent (skip files already present and valid).
- Lenta only when explicitly requested: its licence is unverified and it's for internal stress tests only.
- `data/README.md` with source, citation (Gerber, Green & Larimer 2008; Liu et al. 2021), licence
  (CC0; CC BY 4.0) and size.

## Plan

- [ ] Confirm stable direct-download URLs for both files
- [ ] Write the download script (or a `data` make target)
- [ ] Download once, pin checksums
- [ ] Optional Lenta fetch behind a flag
- [ ] Write `data/README.md`

## Acceptance criteria

- [ ] One command fetches GGL and ASOS into `data/raw/` from a clean checkout
- [ ] A corrupted file fails the checksum check with a clear error
- [ ] Re-running is a no-op
- [ ] Lenta is not downloaded unless requested
- [ ] `data/README.md` has URL, licence, citation and size for each source
