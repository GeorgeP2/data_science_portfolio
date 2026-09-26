# T06: Open-Meteo weather features with a local cache

**Phase:** 1 Data · **Estimate:** 1.5 h · **Depends on:** T01

## Ask

Fetch historical temperature, solar radiation and wind for a set of UK locations from Open-Meteo, cache
them and build a national weather feature (e.g. population-weighted temperature).

## Why

Weather is the main driver of demand after calendar effects. The API is rate-limited, so fetch the
archive once and reuse it.

## How

- A fixed list of locations with population weights (e.g. major GB cities) in `config.yaml`.
- Hourly archive → cache as Parquet; upsample to half-hourly.
- London location(s) for the household model.
- Incremental fetch for recent days, for the daily run. Use the forecast endpoint for next-day
  features at inference and note the difference between actual and forecast weather in backtests.

## Plan

- [ ] Choose locations and weights
- [ ] Archive fetch with retry/backoff and cache
- [ ] Half-hourly alignment
- [ ] National weighted feature
- [ ] `data/README.md` Open-Meteo section, including the non-commercial note

## Acceptance criteria

- [ ] A second run makes no API calls for already-cached ranges
- [ ] Weather covers the full NESO and LCL training ranges with no gaps (or gaps listed)
- [ ] Backtests document whether they use actual or forecast weather
