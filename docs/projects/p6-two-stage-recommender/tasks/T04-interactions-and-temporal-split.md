# T04: Interaction definition and global temporal split

**Phase:** 1 Data · **Estimate:** 2 h · **Depends on:** T03

## Ask

Define the positive interaction and build a global temporal train/validation/test split.

## Why

The brief rules out random splits. A leakage-free split is what makes every metric trustworthy.

## How

- Positive = like, or listen with capped `played_ratio` above a threshold chosen from T03 (in
  `config.yaml`). Either cap `played_ratio` at 1 or keep a replay-count feature; state which.
- Dislikes and unlikes are never positives; keep them for ranker features.
- Global cut-offs by timestamp, following the Yambda benchmark's recipe (confirm its exact
  train/test windows and any gap). Validation is a window before test, used for tuning.
- Cut on bin boundaries so events in the same 5-second bin never straddle a split.
- Cold-start items: tracks in test with no train interactions. Keep `is_organic` on every row.
- Write to `data/processed/` as Parquet.

## Plan

- [ ] Positive definition + replay handling
- [ ] Split cut-offs from config
- [ ] Cold-start flags
- [ ] Leakage tests

## Acceptance criteria

- [ ] Max train timestamp < min validation timestamp < min test timestamp
- [ ] No 5-second bin appears in more than one split
- [ ] Cold-start track count and share of test events are reported
- [ ] Split is deterministic and regenerates from one command
