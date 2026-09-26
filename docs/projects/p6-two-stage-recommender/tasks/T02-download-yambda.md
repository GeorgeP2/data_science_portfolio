# T02: Download script for Yambda 50M

**Phase:** 0 Setup · **Estimate:** 1.5 h · **Depends on:** T01

## Ask

Script the download of the Yambda 50M-event version (interactions + audio embeddings) into
`data/raw/yambda/`, with pinned checksums.

## Why

Raw data is never committed. A scripted, checksummed download is the only route to reproducing any
number in the project. Starting at 50M keeps iteration fast.

## How

- `huggingface_hub` download of the 50M files. Confirm the file layout (per-event-type files vs one
  multi-event file, flat vs sequential format) before writing the script.
- Size is a config parameter so the stretch task can switch to 500M without code changes.
- SHA-256 per file; idempotent.
- `data/README.md`: source, citation, Apache 2.0, size on disk.

## Plan

- [ ] Inspect the Hugging Face repo structure
- [ ] Write the download script (or `make data` target)
- [ ] Download, record and pin checksums
- [ ] Write `data/README.md`

## Acceptance criteria

- [ ] One command downloads the 50M version and audio embeddings from a clean checkout
- [ ] Re-running is a no-op when files are present and valid
- [ ] Changing the size in `config.yaml` selects a different version without code changes
- [ ] `data/README.md` has URL, licence, citation and size
