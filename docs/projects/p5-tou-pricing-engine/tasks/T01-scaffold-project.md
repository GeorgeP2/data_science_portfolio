# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the project folder with `make new-project` and set up its config and dependencies.

## Why

Every later task needs a package to import from, a `config.yaml` for tunables and a passing
`make check`. The generator keeps numbering, package naming and the README table consistent.

## How

- `make new-project name="Time-of-Use Pricing Engine" category=<closest category>`. The package will
  be `time_of_use_pricing_engine`. There is no optimisation/pricing category; pick the closest
  rather than adding one unasked.
- Dependencies: an LP/MIP or CP-SAT solver (`ortools`), `hypothesis` for property tests, `streamlit`
  (the `app` extra), and `pymc` only if the hierarchical route is taken in T08.
- Copy the headline questions and data table from `brief.md` into the project README.

## Plan

- [ ] Re-check every dataset URL and licence (Octopus has no explicit licence; Open Bandit licence is "per paper")
- [ ] Run `make new-project`
- [ ] Add and install dependencies
- [ ] Seed `config.yaml` with `seed`, data paths, and empty `simulator`, `optimiser`, `bandit`, `ope` sections
- [ ] Paste headline questions and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] Project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import time_of_use_pricing_engine"` works from the project folder
- [ ] `make check` passes
- [ ] README states the headline questions and data sources with licences
