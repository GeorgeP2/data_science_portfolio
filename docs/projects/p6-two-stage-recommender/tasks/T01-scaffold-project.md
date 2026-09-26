# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the project folder with `make new-project` and set up its config and dependencies.

## Why

Every later task needs a package to import from, a `config.yaml` for tunables and a passing
`make check`. The generator keeps numbering, package naming and the README table consistent.

## How

- `make new-project name="Two-Stage Music Recommender" category=recsys`. Package:
  `two_stage_music_recommender`.
- Dependencies: `polars`, `pyarrow`, `implicit`, `torch` (`dl` extra), `faiss-cpu` or `hnswlib`,
  `lightgbm` (`ml` extra), `fastapi`/`uvicorn` (`app` extra), `huggingface_hub`. `duckdb` only if the
  stretch task is picked up.
- Copy the headline questions and data table from `brief.md` into the project README.

## Plan

- [ ] Re-check the Yambda URL, licence and available sizes
- [ ] Run `make new-project`
- [ ] Add and install dependencies
- [ ] Seed `config.yaml` with `seed`, data size (`50m`), paths and empty model sections
- [ ] Paste headline questions and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] Project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import two_stage_music_recommender"` works from the project folder
- [ ] `make check` passes
- [ ] README states the headline questions and the data source with licence
