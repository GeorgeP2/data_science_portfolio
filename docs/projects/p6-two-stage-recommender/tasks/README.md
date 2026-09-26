# P6 tasks

Atomic tasks for the [Two-Stage Music Recommender](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-download-yambda.md) | Download Yambda 50M | 0 Setup | 1.5 h | T01 |
| [T03](T03-profile-data.md) | Profile the data | 1 Data | 2 h | T02 |
| [T04](T04-interactions-and-temporal-split.md) | Interactions + global temporal split | 1 Data | 2 h | T03 |
| [T05](T05-evaluation-module.md) | Evaluation module | 1 Data | 2 h | T04 |
| [T06](T06-baselines.md) | Baselines: popular, recent-popular, item-kNN | 2 Retrieval | 2 h | T05 |
| [T07](T07-als-retrieval.md) | ALS retrieval | 2 Retrieval | 2 h | T05 |
| [T08](T08-two-tower-model.md) | Two-tower model with audio embeddings | 2 Retrieval | 4 h | T04, T05 |
| [T09](T09-ann-index.md) | ANN index | 2 Retrieval | 1.5 h | T08 |
| [T10](T10-ranker-features.md) | Ranker candidates and features | 3 Ranking | 3 h | T07, T09 |
| [T11](T11-lightgbm-ranker.md) | LightGBM LambdaRank ranker | 3 Ranking | 2 h | T10 |
| [T12](T12-metrics-table.md) | Metrics table | 3 Ranking | 1 h | T06, T07, T08, T11 |
| [T13](T13-organic-feedback-loop-analysis.md) | Organic vs recommended + feedback-loop write-up | 4 Analysis | 2.5 h | T03, T12 |
| [T14](T14-replay-ab-simulation.md) | Replay-based simulated A/B | 4 Analysis | 2.5 h | T11 |
| [T15](T15-serving-api.md) | Serving API with cache + online ranking | 5 Serving | 2.5 h | T09, T11 |
| [T16](T16-latency-test.md) | p95 latency test | 5 Serving | 1 h | T15 |
| [T17](T17-dockerfile.md) | Dockerfile + local run | 5 Serving | 1 h | T15 |
| [T18](T18-design-decisions-writeup.md) | Design decisions write-up | 6 Write-up | 2 h | T08, T13, T15, T16 |
| [T19](T19-readme.md) | Project README | 6 Write-up | 1.5 h | T12–T14, T16–T18 |
| [T20](T20-stretch-scale-500m.md) | *Stretch:* scale to 500M | Stretch | 4 h | T12 |
| [T21](T21-stretch-diversity-reranking.md) | *Stretch:* diversity re-ranking | Stretch | 3 h | T11 |

**Total:** ~37 h must-have against a ~30 h time box. If it runs over, cut in this order:
1. T08: use one negative-sampling scheme and argue the choice from the literature (−1 h).
2. T13: keep the descriptive comparison, drop the organic-only retrain (−1 h).
3. T06: drop item-kNN, keep the two popularity baselines (−1 h).
4. T10: start with retrieval-score and popularity features only; add groups while time allows (−1 h).
5. T14: drop the organic-only replay variant (−0.5 h).

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| Metrics table: baselines → ALS → two-tower → +ranker, with cold-start and organic splits | T05, T06, T07, T08, T11, T12 |
| Serving API with a latency test | T15, T16 |
| Short write-up on feedback loops using the `is_organic` analysis | T13 |
