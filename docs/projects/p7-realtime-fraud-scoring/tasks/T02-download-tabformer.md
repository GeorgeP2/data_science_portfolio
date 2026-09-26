# T02: Download script for IBM TabFormer transactions

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Write a script that downloads the TabFormer card transactions into `data/raw/tabformer/` and checks
them against a pinned checksum.

## Why

The data licence is unverified, so the data can't be redistributed. A scripted, checksummed download
is the only way a reader can reproduce the results.

## How

- Confirm the current download route (Box link or Git LFS in the IBM/TabFormer repo) and whether it
  can be fetched non-interactively. If it can't, document the manual step precisely.
- Streaming download, SHA-256 check, idempotent, decompress into `data/raw/tabformer/`.
- `data/README.md`: source, citation, "code Apache 2.0, data licence unverified, do not redistribute",
  and a clear statement that the data is synthetic.

## Plan

- [ ] Confirm the download route
- [ ] Write the download script (or a `make data` target)
- [ ] Download once, pin the checksum
- [ ] Write the TabFormer section of `data/README.md`

## Acceptance criteria

- [ ] One command (or one documented manual step plus one command) produces the raw CSV
- [ ] A corrupted file fails the checksum check with a clear error
- [ ] Re-running is a no-op when the file is already present
- [ ] `git ls-files data/` shows no raw data
