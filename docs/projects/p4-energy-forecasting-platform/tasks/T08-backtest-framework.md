# T08: Rolling backtest and metrics

**Phase:** 2 National model · **Estimate:** 2 h · **Depends on:** T02, T03

## Ask

Build a rolling-origin backtest for next-day forecasts with point and probabilistic metrics.

## Why

Every model comparison, and the promotion rule in the Prefect flow, uses this. The backtest window is
one of the design decisions to write up.

## How

- Define "next day" precisely: a forecast issued at a fixed time (e.g. 09:00) for the next day's
  settlement periods, using only data available at issue time.
- Rolling origins over a configurable window (in `config.yaml`); expanding or sliding training window.
- Metrics: MAE, MAPE, pinball loss per quantile, empirical interval coverage (50/80/90%), interval
  width. Put generic ones in `portfolio.evaluation` if they aren't there already.

## Plan

- [ ] Define and document the issue time and horizon
- [ ] Backtest splitter with a leakage test
- [ ] Metrics
- [ ] Results writer to `outputs/metrics.json`

## Acceptance criteria

- [ ] A test proves no training row is later than the issue time for each origin
- [ ] Metrics include MAE, pinball loss and coverage at 50/80/90%
- [ ] The same model and config give identical backtest metrics on re-run
