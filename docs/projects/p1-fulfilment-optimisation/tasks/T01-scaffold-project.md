# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create `projects/01-fulfilment-optimisation/` with `make new-project` and set up its config and dependencies.

## Why

Every later task needs a package to import from, a `config.yaml` for tunables and a passing `make check`.
Using the generator keeps numbering, package naming and the README table consistent.

## How

- `make new-project name="Fulfilment Optimisation" category=<closest category>` (there is no OR
  category yet; pick the closest rather than adding one unasked). Package: `fulfilment_optimisation`.
- Add the project's dependencies (`ortools`, `fastapi`, `uvicorn`, `pydantic`) where the template
  expects them. `simpy` only if the stretch task is picked up.
- Copy the headline question and the data table from `brief.md` into the project README.

## Plan

- [ ] Re-check the three dataset URLs and licences (brief flags two as *unverified*)
- [ ] Run `make new-project`
- [ ] Add dependencies and install them
- [ ] Seed `config.yaml` with `seed`, `data` paths and an empty `solvers` section
- [ ] Paste headline question and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] `projects/01-fulfilment-optimisation/` exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import fulfilment_optimisation"` works from the project folder
- [ ] `make check` passes
- [ ] README states the headline question and data sources with licences
