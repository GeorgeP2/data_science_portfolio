# T12: Metrics table

**Phase:** 3 Ranking · **Estimate:** 1 h · **Depends on:** T06, T07, T08, T11

## Ask

Produce the headline metrics table: baselines → ALS → two-tower → +ranker, with overall, cold-start,
organic and recommended columns, plus coverage and popularity bias.

## Why

The first "Done when" item, and the answer to headline questions 1 and 2.

## How

- Generated from saved metrics in `outputs/`, never typed by hand.
- Written to `docs/projects/p6-two-stage-recommender/results/` and the project README.

## Plan

- [ ] Aggregation script
- [ ] Table in Markdown
- [ ] Sanity-check ordering and outliers

## Acceptance criteria

- [ ] Rows: most-popular, recent-popular, item-kNN, ALS, two-tower, two-tower + ranker
- [ ] Columns: recall@k and NDCG@k for overall, cold-start, organic, recommended; coverage; popularity bias
- [ ] Table regenerates from one command
