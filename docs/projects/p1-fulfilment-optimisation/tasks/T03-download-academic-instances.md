# T03: Download script for Henn & Wäscher and Foodmart instances

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Script the download of the Henn & Wäscher (2012) batching instances (`obsp_instances.zip`) and the
Arbex Valle et al. Foodmart instances into `data/raw/`, with pinned checksums.

## Why

Both licences are unstated, so the instances can't be vendored. A script is the only way a reader can
reproduce the benchmark table.

## How

- Same pattern as T02: streaming download, SHA-256 check, idempotent, unzip into
  `data/raw/henn_waescher/` and `data/raw/foodmart/`.
- Download any published best-known-value tables alongside, or transcribe them into a small committed
  CSV with a citation (numbers from a paper are fine to cite; the instance files are not committed).

## Plan

- [ ] Confirm both URLs still resolve
- [ ] Write the download script(s)
- [ ] Pin checksums
- [ ] Record best-known values per instance with their source
- [ ] Add both sources to `data/README.md` with a "do not redistribute" note

## Acceptance criteria

- [ ] One command fetches and unpacks both instance sets
- [ ] No instance file is tracked by git (`git ls-files data/` is empty)
- [ ] A best-known-value table exists with a citation per value
- [ ] `data/README.md` states the licence is unverified and why files are fetched, not vendored
