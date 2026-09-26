# T19: `make analysis` pipeline

**Phase:** 4 Pipeline and write-up · **Estimate:** 1.5 h · **Depends on:** T04–T06, T10, T12, T17, T18

## Ask

Wire every analysis into one notebook-free command, `make analysis`, that downloads data and writes
all figures, tables, metrics and the memo.

## Why

"Done when" requires a notebook-free reproducible pipeline. It also guarantees the memo's numbers
come from code, not copy-paste.

## How

- A project-level `Makefile` (the root one has no `analysis` target) calling
  `PYTHONPATH=src python -m experimentation_uplift.<step>` for each stage.
- Steps are idempotent and skip work whose outputs are newer than their inputs.
- Metrics via `portfolio.evaluation` into `outputs/metrics.json`; figures via `portfolio.plotting.save_fig`.
- Notebooks, if any, are exploration only and not part of the pipeline.

## Plan

- [ ] Entrypoint per stage
- [ ] Makefile target
- [ ] Clean-clone run

## Acceptance criteria

- [ ] `make analysis` from a clean clone produces every figure, table and the memo
- [ ] No step imports or executes a notebook
- [ ] Running it twice gives identical outputs
