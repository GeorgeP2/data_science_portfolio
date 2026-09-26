# T04: Download the Open Bandit Dataset

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** T01

## Ask

Script the download (413 MB) of the Open Bandit Dataset into `data/raw/open_bandit/` with a pinned
checksum, and load both logging policies' logs.

## Why

It's the only data in the project with two real logging policies and true propensities, which is what
lets the OPE estimators be validated against ground truth (T15).

## How

- Streaming download, SHA-256 check, idempotent, unzip.
- Loader returning actions, positions, rewards (clicks), propensities and context per policy
  (`random`, `bts`) and campaign. Confirm the file layout on download.
- Licence is CC BY 4.0 per the paper, research use; confirm and record in `data/README.md`.

## Plan

- [ ] Download script with checksum
- [ ] Loader
- [ ] Summary: rows, actions, click rate per policy × campaign

## Acceptance criteria

- [ ] One command downloads and unpacks the dataset
- [ ] Loader returns both policies with propensities in (0, 1]
- [ ] Summary numbers are saved and match the paper's reported dataset size (~26M rows) or the difference is explained
