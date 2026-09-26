# T09: Seasonal naive and LightGBM national models

**Phase:** 2 National model · **Estimate:** 2 h · **Depends on:** T06, T07, T08

## Ask

Implement the first two rungs of the model ladder: seasonal naive, and LightGBM with calendar and
weather features.

## Why

Seasonal naive is the bar any model must clear. LightGBM with features is the practical workhorse the
probabilistic model builds on.

## How

- Seasonal naive: same period one week earlier (state the choice; compare with one day earlier).
- Features: period of day, day of week, bank holidays, lagged demand available at issue time,
  weighted temperature, solar radiation, wind. Embedded solar/wind in NESO data are modelled, not
  metered; note how that affects their use as features.
- Hyperparameters in `config.yaml`; log to MLflow once T14 exists.

## Plan

- [ ] Seasonal naive
- [ ] Feature builder with a no-leakage test
- [ ] LightGBM point model
- [ ] Backtest both

## Acceptance criteria

- [ ] Both run through the T08 backtest
- [ ] LightGBM beats seasonal naive on MAE, or the result is reported honestly
- [ ] Feature builder test confirms no feature uses data after the issue time
