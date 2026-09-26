# T03: Download script for Feedzai BAF

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Script the download of the Feedzai Bank Account Fraud (BAF) dataset from Kaggle into `data/raw/baf/`.

## Why

The fairness companion runs on BAF. Kaggle needs a login, so the script must use the Kaggle API with
the reader's own credentials.

## How

- Kaggle API (`kaggle datasets download`); credentials from `~/.kaggle/kaggle.json`, never committed.
- Pin checksums of the extracted CSVs. Confirm the number of variants (brief says 6 × 1M rows) and
  record which variant(s) the companion uses (Base unless there's a reason otherwise).
- `data/README.md`: source, NeurIPS 2022 citation, Apache 2.0 plus the "contact Feedzai for
  commercial use" clause, and that use here is non-commercial.

## Plan

- [ ] Write the download script
- [ ] Pin checksums
- [ ] Choose and record the variant(s)
- [ ] Write the BAF section of `data/README.md`

## Acceptance criteria

- [ ] With Kaggle credentials set, one command fetches and extracts the dataset
- [ ] Missing credentials fail with a message explaining the setup step
- [ ] `data/README.md` states the licence and the commercial-use clause
