# T21 (stretch): Diversity re-ranking stage

**Phase:** Stretch · **Estimate:** 3 h · **Depends on:** T11

## Ask

Add a re-ranking stage (e.g. MMR over item embeddings) after the ranker and measure the
accuracy–diversity trade-off.

## Why

Links to the feedback-loop story: re-ranking is one lever against catalogue narrowing.

## How

- MMR with a diversity weight λ in config, using two-tower item embeddings for similarity.
- Sweep λ; measure NDCG@k, intra-list diversity, coverage and popularity bias.

## Plan

- [ ] Only start once T01–T19 are done
- [ ] Implement MMR
- [ ] λ sweep
- [ ] Trade-off chart

## Acceptance criteria

- [ ] λ = 0 reproduces the ranker's output exactly
- [ ] Trade-off chart of NDCG@k vs diversity/coverage saved to `reports/figures/`
- [ ] A recommended λ is stated with its reason
