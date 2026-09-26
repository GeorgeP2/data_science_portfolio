# CLAUDE.md

Data science / ML / AI portfolio. Monorepo: one self-contained folder per project under `projects/`,
shared utilities in `src/portfolio/`.

## Scope

- `docs/Principal ML Engineer Roadmap.md` (git-ignored, private) drives what gets built. Don't create
  or flesh out projects that aren't on the roadmap; ask first.
- Per-project planning lives in `docs/projects/pN-name/` (`brief.md`, `results/`); code lives in
  `projects/NN-name/`. Task breakdowns go in `docs/projects/pN-name/tasks/`, which is git-ignored
  (private working notes). Committed docs must not mention the job search (target companies,
  applications, market analysis).
- Keep changes to what was asked. Scaffolding and examples beyond the request aren't wanted.

## Commands

```bash
make setup          # create .venv, install core+dev+notebooks, install pre-commit hooks
make check          # lint + typecheck + tests (same as CI)
make format         # ruff fix + format
make new-project name="Title" category=ml   # scaffold from projects/_template
```

Use `.venv/bin/...` for tools. Optional dependency extras: `ml`, `dl`, `nlp`, `llm`, `tracking`, `app`.

## Non-obvious details

- New projects come from `make new-project` (it numbers the folder, renames the package and adds a
  row to the README table between the `<!-- projects:end -->` marker). Don't copy `_template` by hand.
- `projects/_template/` contains `{{placeholders}}`, so ruff and pytest exclude it on purpose.
- Root `conftest.py` adds every `projects/*/src` to `sys.path` for tests, so each project's
  package name must be unique.
- Run project code from its folder: `PYTHONPATH=src python -m <package>.train`.
- `data/` and `outputs/` inside projects are git-ignored; `reports/figures/` is committed.
- Notebook outputs are stripped by nbstripout on commit.

## Conventions

Follow `docs/conventions.md`: tunables in `config.yaml` (`portfolio.load_config`), seed via
`portfolio.seed_everything`, paths via `portfolio.ProjectPaths`, metrics via `portfolio.evaluation`.
Anything used by two or more projects belongs in `src/portfolio/`.
