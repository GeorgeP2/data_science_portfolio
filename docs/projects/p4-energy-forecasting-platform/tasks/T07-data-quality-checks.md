# T07: Data-quality checks

**Phase:** 1 Data · **Estimate:** 1.5 h · **Depends on:** T02, T03, T04, T06

## Ask

Add Pandera schemas for NESO, LCL and weather data, and run them as a validation step.

## Why

The Prefect flow validates before training. Bad data should stop a run instead of reaching a model.

## How

- Schemas: types, ranges (e.g. demand > 0, kWh ≥ 0), unique `(timestamp)` / `(household, timestamp)`,
  expected periods per day using T03.
- Failures raise with a readable summary; warnings for soft issues (e.g. short gaps).

## Plan

- [ ] Schemas per dataset
- [ ] `validate(dataset)` entrypoint
- [ ] Tests with deliberately broken fixtures

## Acceptance criteria

- [ ] All three datasets pass validation on the real data (or known issues are listed and handled)
- [ ] A fixture with a duplicate timestamp and a fixture with a wrong period count both fail
- [ ] Validation runs in `make check` against fixtures
