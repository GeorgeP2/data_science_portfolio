# T11: LightGBM LambdaRank ranker

**Phase:** 3 Ranking · **Estimate:** 2 h · **Depends on:** T10

## Ask

Train a LightGBM LambdaRank model on the T10 tables and score the full two-stage pipeline.

## Why

Answers headline question 1: how much does a learned ranker improve recall@k and NDCG@k over
retrieval alone?

## How

- `lambdarank` objective, grouped by user; early stopping on validation NDCG@k.
- Hyperparameters in `config.yaml`; a small sweep only.
- Feature importance (gain) and one ablation (drop recency or cross features).

## Plan

- [ ] Train with early stopping
- [ ] Score on test with T05, all slices
- [ ] Feature importance + one ablation

## Acceptance criteria

- [ ] Two-stage NDCG@k beats the best retriever on test, or the shortfall is explained
- [ ] Metrics saved for all slices
- [ ] Feature importance plot saved to `reports/figures/`
