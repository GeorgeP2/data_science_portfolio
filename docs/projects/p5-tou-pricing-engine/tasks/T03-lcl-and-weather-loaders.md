# T03: LCL and weather loaders (shared with Project 4)

**Phase:** 0 Setup · **Estimate:** 2 h · **Depends on:** T01

## Ask

Load the Low Carbon London smart-meter data (ToU and Std households, 2013 price schedule) and
matching London weather, via loaders in `src/portfolio/`.

## Why

Project 4 uses the same LCL and Open-Meteo data. CLAUDE.md says anything used by two projects belongs
in `src/portfolio/`, so these loaders must not live in either project's package.

## How

- If Project 4 already built the loaders, reuse them and only add what P5 needs (the price-signal
  schedule, household tariff group). Otherwise write them in `src/portfolio/` now, following
  Project 4's plan: download script, partitioned parquet, sample households for development.
- Weather: the brief needs weather-driven baseline demand but lists no weather source; use Project 4's
  Open-Meteo source for London.
- Load the 2013 ToU price-signal schedule (High / Normal / Low, 67.20p / 11.76p / 3.99p) into a
  half-hourly table.

## Plan

- [ ] Check whether Project 4's loaders exist; reuse or write them in `src/portfolio/`
- [ ] Add price-signal schedule loader
- [ ] Add London weather for Nov 2011–Feb 2014
- [ ] Tests with small fixtures

## Acceptance criteria

- [ ] LCL, price-signal and weather loaders live in `src/portfolio/` and are mypy-clean
- [ ] Price-signal table covers the whole 2013 trial with exactly three price levels
- [ ] Tests run without the raw data
- [ ] `data/README.md` credits LCL (CC BY) and Open-Meteo (CC BY 4.0)
