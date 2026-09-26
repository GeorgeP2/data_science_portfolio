# T03: Settlement periods and clock-change days

**Phase:** 1 Data · **Estimate:** 1.5 h · **Depends on:** T01

## Ask

Write a utility that converts (settlement date, settlement period) into UTC timestamps, handling
clock-change days with 46 or 50 periods.

## Why

Clock-change days break naive "48 periods a day" logic and silently misalign features and targets.
Project 5 uses the same half-hourly GB conventions, so this belongs in `src/portfolio/` (anything used
by two or more projects goes there).

## How

- Use `zoneinfo("Europe/London")`: period 1 starts at local midnight; count periods in UTC.
- Validation helper: expected number of periods for a given date (46 / 48 / 50).
- Put it in `src/portfolio/` (e.g. `portfolio.energy.settlement`) with tests and type hints.

## Plan

- [ ] Implement `period_to_utc` and `periods_in_day`
- [ ] Tests on spring-forward and autumn-back days in several years
- [ ] Apply to NESO data (T02) and check period counts per day

## Acceptance criteria

- [ ] Tests cover a 46-period day, a 50-period day and a normal day
- [ ] NESO data has no duplicate or missing UTC timestamps after conversion (or gaps are listed)
- [ ] Function lives in `src/portfolio/` and passes mypy
