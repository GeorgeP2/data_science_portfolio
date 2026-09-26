# T03: Download DAPR, process guides and rulings

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Script the download of DAPR (Sept 2026 edition), the PGD process guides and the DAB rulings from the
`delay-attribution-board` container, and confirm their licence.

## Why

These are the retrieval corpus. The licence is unconfirmed, and it decides whether any text can be
vendored or must always be fetched.

## How

- Same pattern as T02: list, download, checksum, idempotent.
- Find the licence statement. Until it's confirmed, fetch only and vendor nothing.
- Record counts found vs the brief (~26 PGDs, ~52 rulings in DAB001–053) and note gaps in numbering.

## Plan

- [ ] Download script
- [ ] Confirm the licence and record where the confirmation came from
- [ ] Inventory: document, edition/date, pages
- [ ] `data/README.md` section

## Acceptance criteria

- [ ] One command fetches all rulebook documents with checksums
- [ ] Licence status is written down with a link; nothing is vendored unless confirmed OGL
- [ ] Inventory lists every document and any missing numbers in the PGD/DAB ranges
