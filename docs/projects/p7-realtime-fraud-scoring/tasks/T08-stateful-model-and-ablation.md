# T08: Stateful-feature model and ablation

**Phase:** 1 Offline model · **Estimate:** 1.5 h · **Depends on:** T06, T07

## Ask

Train LightGBM on static + stateful features and measure what each stateful feature group adds.

## Why

Answers the first half of headline question 2: how much stateful features add over static ones.

## How

- Same training entrypoint with `--features static+stateful`.
- Ablation: drop one group at a time (velocity windows, time since last, novelty, z-score).
- Compare on validation PR-AUC, recall at fixed FPR and expected cost (T09).

## Plan

- [ ] Train the full model
- [ ] Ablation runs
- [ ] Table into `docs/projects/p7-realtime-fraud-scoring/results/`

## Acceptance criteria

- [ ] Table shows static vs full vs each ablation on the same metrics
- [ ] Final model is evaluated once on the test split and saved as the artefact the scorer loads
