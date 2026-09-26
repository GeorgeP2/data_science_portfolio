# T10: Ranker candidates and features

**Phase:** 3 Ranking · **Estimate:** 3 h · **Depends on:** T07, T09

## Ask

Build the ranker's training and evaluation tables: retrieval candidates per user, labels, and user,
item, cross and recency features.

## Why

The ranker can only reorder what retrieval returns, and it's only as good as its features. This is
where most of the two-stage gain comes from.

## How

- Candidates: union of ALS and two-tower top-N per user; keep a `source` column. Report candidate
  recall@N of the union.
- Labels: positive if the candidate is a positive in the label window (T04 definition).
- Ranker training uses a window *before* validation, with features computed only from data before
  that window, so features never see the labels.
- Features: user (activity, like/dislike rates, organic share), item (popularity, recent trend,
  skip rate from `played_ratio`, cold flag), cross (retrieval scores and ranks, similarity to recent
  history, artist/album affinity if available), recency (time since last listen of the item/artist).
- Polars only; write to Parquet.

## Plan

- [ ] Candidate union and recall@N
- [ ] Label window and feature cut-off
- [ ] Feature groups
- [ ] Leakage tests

## Acceptance criteria

- [ ] Every feature is computed from data strictly before its label window (tested)
- [ ] Candidate recall@N of the union is reported and ≥ each source alone
- [ ] Feature tables build from one command for train, validation and test
