# T14: MLflow tracking and model registry

**Phase:** 4 Platform · **Estimate:** 1.5 h · **Depends on:** T10

## Ask

Log national model runs (params, metrics, artefacts) to MLflow, and register models with a
`production` alias.

## Why

The daily run's history must be visible in MLflow ("Done when"), and promotion needs a registry.

## How

- Local MLflow tracking with a SQLite/file backend under `outputs/` (git-ignored).
- Log config, backtest metrics, the calibration plot and the model.
- Registered model with a `production` alias, plus a helper to load the current production model.

## Plan

- [ ] Tracking setup, with the URI in `config.yaml`
- [ ] Logging in the training entrypoint
- [ ] Registry + alias helpers
- [ ] Test against a temporary tracking directory

## Acceptance criteria

- [ ] A training run appears in the MLflow UI with params, metrics and plots
- [ ] `load_production_model()` returns the aliased model
- [ ] Tests run against a temporary MLflow store
