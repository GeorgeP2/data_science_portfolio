# T06: Baselines: most-popular, recent-popular, item-kNN

**Phase:** 2 Retrieval · **Estimate:** 2 h · **Depends on:** T05

## Ask

Implement and score the three baselines.

## Why

The first rows of the metrics table. A two-stage system only matters if it clearly beats these.

## How

- Most-popular: train-period counts. Recent-popular: counts over the last window (length in config).
- Item-kNN: cosine similarity on the sparse user–item matrix, top-N neighbours per item.
- Decide whether to filter already-consumed items and apply the choice to every model.

## Plan

- [ ] Most-popular and recent-popular
- [ ] Item-kNN
- [ ] Score with T05, save to `outputs/`

## Acceptance criteria

- [ ] All three produce top-k lists for every test user
- [ ] Metrics for each are saved, including all slices
- [ ] Cold-start recall is reported for each (expected near zero)
