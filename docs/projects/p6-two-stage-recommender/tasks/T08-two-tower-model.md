# T08: Two-tower model with audio embeddings

**Phase:** 2 Retrieval · **Estimate:** 4 h · **Depends on:** T04, T05

## Ask

Train a PyTorch two-tower retriever whose item tower takes audio embeddings, so cold-start tracks
get usable vectors.

## Why

Answers headline question 2: do audio embeddings rescue tracks collaborative filtering can't
recommend? The negative-sampling comparison feeds a design decision in the brief.

## How

- User tower: user ID embedding + pooled recent history. Item tower: track ID embedding (dropped
  for cold items, with ID dropout in training) + MLP on the audio embedding.
- Default: in-batch negatives with logQ popularity correction. Compare one alternative (e.g. mixed
  in-batch + uniform random negatives).
- Train on a sample if needed; batch size, dims and epochs in `config.yaml`.
- Tracks without an audio embedding (per T03) fall back to ID only; report how many.

## Plan

- [ ] Dataset/dataloader from Parquet
- [ ] Towers and loss
- [ ] Training loop with validation early stopping
- [ ] Negative-sampling comparison (2 variants)
- [ ] Export user and item embeddings

## Acceptance criteria

- [ ] A seeded run reproduces validation metrics within a stated tolerance
- [ ] Cold-start recall@k is reported against ALS and popularity
- [ ] Both negative-sampling variants are scored and the choice is justified
- [ ] Every track with an audio embedding gets an item vector, including cold-start ones
