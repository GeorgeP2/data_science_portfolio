# T15: Prefect flow with promotion gate

**Phase:** 4 Platform · **Estimate:** 2.5 h · **Depends on:** T02, T07, T10, T14

## Ask

Build the Prefect flow ingest → validate → train → evaluate → register (MLflow) → promote, where a
candidate is promoted only if it beats the current production model on a rolling backtest.

## Why

This is the MLOps core of the project. The promotion rule is a design decision to write up.

## How

- Each step is a Prefect task; ingestion has retries.
- Promotion rule in `config.yaml`, e.g. the candidate beats production on pinball loss over the last
  N days *and* 90% coverage stays within a tolerance. Both models are scored on the same window.
- With no production model yet, the first run promotes automatically and logs why.

## Plan

- [ ] Tasks and flow
- [ ] Promotion rule and comparison
- [ ] Test: a worse candidate isn't promoted, a better one is
- [ ] Run end to end locally

## Acceptance criteria

- [ ] `PYTHONPATH=src python -m energy_demand_forecasting_platform.flow` runs end to end
- [ ] A deliberately worse candidate is registered but not promoted (test)
- [ ] The promotion decision and both scores are logged to MLflow
