# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the code folder with `make new-project name="Experimentation & Uplift" category=stats` and set
up its config and dependencies. The folder number is assigned by `make new-project`; the package is
`experimentation_uplift`.

## Why

Every later task needs a package to import from, a `config.yaml` for tunables and a passing
`make check`. The generator keeps numbering, naming and the README table consistent.

## How

- Dependencies: `statsmodels` (clustered SEs), `econml` (causal forest, DR-learner), `scikit-learn`,
  `pyarrow` (ASOS parquet). `streamlit` comes from the `app` extra if the power calculator uses it.
  `pymc` only if the stretch task is picked up.
- Copy the headline questions and the data table from `brief.md` into the project README.

## Plan

- [ ] Re-check the GGL, ASOS and Lenta URLs and licences (Lenta is flagged *unverified*)
- [ ] Run `make new-project`
- [ ] Add dependencies and install them
- [ ] Seed `config.yaml` with `seed`, data paths, `n_bootstrap` and `alpha`
- [ ] Paste the headline questions and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] Project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import experimentation_uplift"` works from the project folder
- [ ] `make check` passes
- [ ] README states both headline questions and the data sources with licences
