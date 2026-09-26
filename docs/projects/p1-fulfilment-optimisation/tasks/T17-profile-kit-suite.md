# T17: Profile the KIT benchmark suite

**Phase:** 5 Generator · **Estimate:** 2 h · **Depends on:** T02

## Ask

Extract the distributions the generator needs from the KIT suite: layout dimensions, orders per
shift, lines per order, arrival randomness, due dates and storage policies.

## Why

The generator's parameter ranges must come from data, not guesses. Otherwise the "calibrated
generator" claim doesn't hold.

## How

- Stream the 2 GB of JSON (don't load it all at once); flatten to parquet in `data/processed/`.
- Summarise each parameter across the 200 configurations: ranges, quantiles, fitted distribution family.
- A numbered notebook calling into `src/` for the plots.

## Plan

- [ ] Inspect the JSON schema
- [ ] Streaming loader → parquet
- [ ] Per-parameter summaries and fits
- [ ] Notebook with the findings

## Acceptance criteria

- [ ] Loader processes the full suite without exceeding available memory
- [ ] A table of fitted ranges/distributions per generator parameter is saved
- [ ] Notebook runs top to bottom from `data/processed/`
