# T09: Approximate nearest-neighbour index

**Phase:** 2 Retrieval · **Estimate:** 1.5 h · **Depends on:** T08

## Ask

Build a FAISS or HNSW index over two-tower item embeddings for top-k retrieval.

## Why

Exact search over millions of tracks is too slow for serving. The index sets the retrieval stage's
latency budget.

## How

- FAISS (HNSW or IVF) or `hnswlib`; parameters in `config.yaml`.
- Measure ANN recall against exact top-k on a user sample, and query latency.

## Plan

- [ ] Build and persist the index
- [ ] ANN vs exact comparison
- [ ] Latency measurement

## Acceptance criteria

- [ ] ANN top-k overlap with exact search is ≥ 0.95 on a user sample, or the trade-off is stated
- [ ] p95 single-query latency is reported
- [ ] Index builds from one command
