# T06: Build the elasticity modelling dataset

**Phase:** 1 Elasticity · **Estimate:** 2 h · **Depends on:** T03, T05

## Ask

Build a half-hourly table joining ToU households' consumption to the price signal in force, with Std
households as a comparison group, weather and calendar features.

## Why

Elasticity by time of day and household group (T07) needs a clean panel with the price signal
aligned to consumption and a baseline to compare against.

## How

- Filter to the 2013 trial period; align price signals to half-hours.
- Features: time of day, day type, temperature, household group (ACORN if available, otherwise tariff
  group + load-shape cluster, as Project 4 does).
- Use the Std group (or a pre-trial baseline, per T05) as the counterfactual.
- Sample households for development; full run at the end.

## Plan

- [ ] Join consumption, price signal, weather
- [ ] Household grouping
- [ ] Data-quality checks (missing reads, zero-consumption meters)
- [ ] Save to `data/processed/`

## Acceptance criteria

- [ ] Every ToU row has exactly one price level
- [ ] Missing and dropped households are counted and reported
- [ ] Dataset builds from one command
