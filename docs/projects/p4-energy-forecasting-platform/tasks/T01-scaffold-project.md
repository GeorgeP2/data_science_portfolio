# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the project folder with `make new-project name="Energy Demand Forecasting Platform" category=ts`
and set up its config and dependencies.

## Why

Every later task needs an importable package, a `config.yaml` for tunables and a passing `make check`.
The generator keeps numbering, package naming and the README table consistent.

## How

- Package: `energy_demand_forecasting_platform` (derived by `scripts/new_project.py`).
- Existing extras cover LightGBM (`ml`), MLflow (`tracking`), FastAPI and Streamlit (`app`). Add the
  project-specific ones: `pymc`, `prefect`, `evidently`, `pandera`, `pyarrow`.
- Copy the headline questions and data table from `brief.md` into the project README.

## Plan

- [ ] Re-check the dataset URLs and licences (Open-Meteo free tier is non-commercial; Elexon terms unchecked)
- [ ] Run `make new-project`
- [ ] Add and install dependencies
- [ ] Seed `config.yaml` with `seed`, data paths and empty `national`, `household`, `platform` sections
- [ ] Paste headline questions and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] Project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import energy_demand_forecasting_platform"` works from the project folder
- [ ] `make check` passes
- [ ] README states both headline questions and the data sources with licences
