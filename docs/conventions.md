# Project conventions

The goal: any project can be understood in 2 minutes from its README and reproduced with one command.

## Structure

- One folder per project: `projects/NN-kebab-case-name/`. Create it with `make new-project`.
- Pipeline code lives in `src/<package>/` as importable functions — notebooks call into it rather
  than duplicating logic.
- Notebooks are numbered in reading order: `01_eda.ipynb`, `02_modelling.ipynb`, …
- Anything shared by two or more projects moves into `src/portfolio/`.

## Data

- Never commit raw data. `data/` is git-ignored; the project README says exactly how to get it.
- Prefer public datasets with a clear licence (Kaggle, UCI, Hugging Face, government open data).
- Treat `data/raw/` as read-only. Write derived data to `data/processed/`.

## Reproducibility

- All tunable values go in `config.yaml`, loaded with `portfolio.load_config`.
- Call `portfolio.seed_everything(cfg.seed)` at the start of every entrypoint.
- Resolve paths with `portfolio.ProjectPaths` — no hard-coded absolute paths.
- Write metrics to `outputs/metrics.json` using the helpers in `portfolio.evaluation`.

## Quality

- `make check` must pass before pushing (CI runs the same thing).
- Each project has at least a smoke test; test data transforms and feature logic properly.
- Notebook outputs are stripped on commit by `nbstripout`. Save figures you want to show
  with `portfolio.plotting.save_fig` into `reports/figures/`, and embed them in the README.

## README checklist

- [ ] Problem statement and why it matters
- [ ] Data source, size and licence
- [ ] Approach, including the baseline
- [ ] Results table and at least one figure
- [ ] Takeaways and limitations
- [ ] Reproduce section
- [ ] Skills demonstrated
