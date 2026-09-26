# T03: Profile the data

**Phase:** 1 Data · **Estimate:** 2 h · **Depends on:** T02

## Ask

Profile the 50M events: event types, users/tracks, time span, `is_organic` share, `played_ratio`
distribution, 5-second timestamp bins and audio-embedding coverage.

## Why

The brief's gotchas (binned timestamps, `played_ratio` over 100%) and the cold-start story depend on
facts that must be measured, not assumed.

## How

- Polars lazy scans over Parquet; no pandas joins.
- Measure: events per type, organic vs recommended share per type, `played_ratio` quantiles and share
  above 1, share of a user's events that share a timestamp bin, and share of tracks with an audio
  embedding (confirm; the brief quotes ~7.7M of 9.39M tracks in the full dataset).
- `01_eda.ipynb` calls into `src/`.

## Plan

- [ ] Polars loaders in `src/`
- [ ] Summary statistics
- [ ] Notebook with plots
- [ ] Short findings list feeding T04

## Acceptance criteria

- [ ] Notebook runs top to bottom on the 50M version without running out of memory
- [ ] Reports: `is_organic` share, `played_ratio` > 1 share, same-bin event share, embedding coverage
- [ ] Findings list states the decisions T04 needs (listen threshold, replay handling, tie-breaking)
