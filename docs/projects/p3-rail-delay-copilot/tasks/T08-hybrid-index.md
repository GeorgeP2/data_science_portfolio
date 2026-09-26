# T08: Hybrid BM25 + embedding index

**Phase:** 2 Retrieval · **Estimate:** 2 h · **Depends on:** T07

## Ask

Build BM25 and embedding indexes over the chunks and fuse their results.

## Why

Rail jargon and code numbers favour lexical search; paraphrased questions favour embeddings. Hybrid
covers both.

## How

- BM25 over tokenised chunks; embeddings from a small open sentence-transformers model (name in
  config); reciprocal rank fusion.
- Persist both indexes under `data/processed/`.

## Plan

- [ ] BM25 index
- [ ] Embedding index
- [ ] Fusion
- [ ] Retrieval check: ~20 hand-written question → expected-section pairs

## Acceptance criteria

- [ ] `search(query, k)` returns chunks with section citations
- [ ] Recall@5 on the 20-question check is reported for BM25, embeddings and hybrid; hybrid ≥ each alone
- [ ] Index build is one command and deterministic
