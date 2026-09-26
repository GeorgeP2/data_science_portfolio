# Project 6 (optional): Two-Stage Music Recommender

**One line:** a production-shaped recommender on a 2025 industrial music dataset. It has
two-tower retrieval that uses audio embeddings for cold-start, a LightGBM ranker and a serving API
with caching. It also looks at how much of listening the existing recommender *caused*.

**Time box:** weeks 24–26+ (~30 h). Pick this **or** Project 5.

## Headline questions

> 1. How much does a learned ranker on top of retrieval improve recall@k and NDCG@k over
>    popularity and ALS baselines under a strict time-based split?
> 2. Do audio embeddings rescue cold-start tracks that collaborative filtering can't recommend?
> 3. Listens are flagged **organic** vs **recommended**. How different are the two, and what does
>    training on recommended listens do to feedback loops?

## Why this data is different

MovieLens and H&M are the defaults. **Yandex Yambda** (2025) is a large industrial dataset with
rarely available signals:
- **Explicit and implicit feedback together:** listens with played ratio, likes, dislikes, unlikes.
- **An `is_organic` flag** on every event.
- **Pre-computed audio embeddings** for ~7.7M tracks.

It comes in 50M / 500M / 5B-event sizes, so development can start small and scale later.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| [Yandex Yambda](https://huggingface.co/datasets/yandex/yambda) | Up to 4.79B events, 1M users, 9.39M tracks; listens (played ratio), likes/dislikes, `is_organic`, audio embeddings | Hugging Face; start with 50M | Apache 2.0 |
| *Alternative:* [KuaiRand-1K](https://zenodo.org/records/10439422) | 11.7M short-video interactions + 43k **uniformly random exposures** for unbiased evaluation | Zenodo | CC BY-SA 4.0 (share-alike on redistribution) |
| *Alternative:* [RecFlow](https://github.com/RecFlow-ICLR/RecFlow) | Logs from every funnel stage (retrieval → ranking → re-ranking) | USTC share link | CC BY-SA 4.0 |

Use one dataset end to end. A model trained on Yambda **can't** be evaluated on KuaiRand's random
log, because the users and items are different. Choose KuaiRand instead only if unbiased
off-policy evaluation matters more than the music/cold-start story.

## Scope

**Must have**
- **Global temporal split** (as the Yambda benchmark does); no random splits.
- **Baselines:** most-popular, recent-popular and item-kNN.
- **Retrieval:**
  - ALS (implicit)
  - A two-tower model (PyTorch) with audio embeddings in the item tower
  - Top-k retrieval using a FAISS / HNSW (approximate nearest-neighbour) index
- **Ranker:** LightGBM LambdaRank on retrieval candidates with user, item, cross and recency features.
- **Metrics:**
  - recall@k and NDCG@k overall, plus separately for cold-start items and for organic vs recommended events
  - coverage and popularity bias
- **Simulated A/B:** replay-based comparison of the two policies with a confidence interval.
- **Serving:** FastAPI with a precomputed candidate cache and online ranking, plus a p95 latency test.

**Stretch:** scale to the 500M version with Polars/DuckDB; a diversity re-ranking stage.

**Out of scope:** sequence transformers (SASRec etc.) beyond a mention in the write-up.

## Design decisions to write up

- Why two stages: the latency and compute budget per stage.
- Negative sampling choices for the two-tower model.
- What "recommended" events do to offline evaluation (exposure bias).
- Cache invalidation and freshness vs latency.

## Risks and gotchas

- **Scale:** even 50M events need care. Use Parquet + Polars, and don't use pandas for joins.
- **Timestamps are binned to 5 seconds**, so ordering within a bin is ambiguous.
- **`played_ratio` can exceed 100%** (replays), so cap it or model replays explicitly.

## Done when

- [ ] Metrics table: baselines → ALS → two-tower → +ranker, with cold-start and organic splits
- [ ] Serving API with a latency test
- [ ] Short write-up on feedback loops using the `is_organic` analysis
