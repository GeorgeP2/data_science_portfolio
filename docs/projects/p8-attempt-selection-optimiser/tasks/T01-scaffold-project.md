# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the code folder with `make new-project` and set up its config and dependencies.

## Why

Every later task needs a package to import from, a `config.yaml` for tunables and a passing
`make check`. The generator keeps numbering, package naming and the README table consistent.

## How

- `make new-project name="Powerlifting Attempt Selection Optimiser" category=stats` (closest existing
  category). Package: `powerlifting_attempt_selection_optimiser`.
- Dependencies: `pymc`, `arviz`, `scikit-learn`, `lightgbm` (the `ml` extra), `hypothesis` for
  property tests, `streamlit` (the `app` extra).
- Copy the headline questions and data table from `brief.md` into the project README.

## Plan

- [ ] Re-check the OpenPowerlifting URL, licence and download size (the brief flags size and cadence as *unverified*)
- [ ] Run `make new-project`
- [ ] Add dependencies and install them
- [ ] Seed `config.yaml` with `seed`, data paths and the train/test cut-off date
- [ ] Paste headline questions and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] Project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import powerlifting_attempt_selection_optimiser"` works from the project folder
- [ ] `make check` passes
- [ ] README states the headline questions and credits OpenPowerlifting
