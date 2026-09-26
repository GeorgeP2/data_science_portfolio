# T07: ALS retrieval

**Phase:** 2 Retrieval · **Estimate:** 2 h · **Depends on:** T05

## Ask

Train implicit ALS and score it as a retriever.

## Why

ALS is the standard collaborative-filtering retriever. It's the bar the two-tower model must beat,
and the model that can't handle cold-start tracks.

## How

- `implicit` ALS on the confidence-weighted user–item matrix (weights from T04's signal).
- Tune factors, regularisation and alpha on validation; values in `config.yaml`.
- Retrieve top-N candidates per user (N in config) for the ranker, as well as top-k for metrics.

## Plan

- [ ] Matrix build
- [ ] Train + small validation sweep
- [ ] Score with T05
- [ ] Save candidates to `data/processed/`

## Acceptance criteria

- [ ] ALS beats most-popular on overall recall@k
- [ ] Hyperparameters are chosen on validation, not test
- [ ] Candidate recall@N (share of test positives in the candidate set) is reported
