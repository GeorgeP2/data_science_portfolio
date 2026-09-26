# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the project folder with `make new-project` and set up its config and dependencies.

## Why

Every later task needs an importable package, a `config.yaml` for tunables and a passing `make check`.

## How

- `make new-project name="Rail Delay Copilot" category=llm`. Package: `rail_delay_copilot`.
- Dependencies: `duckdb`, a BM25 library, `sentence-transformers`, `anthropic`, the MCP Python SDK,
  `peft`, `transformers`, `scikit-learn`, `sqlglot`. Reuse the repo's `nlp` / `llm` extras where they
  already cover these.
- `config.yaml` sections: `data`, `retrieval`, `sql`, `agent`, `eval`, `classify`. Model IDs are
  config values (e.g. `claude-sonnet-5`, `claude-haiku-4-5-20251001`), never hard-coded.
- `.env.example` with `ANTHROPIC_API_KEY=`; `.env` is git-ignored.

## Plan

- [ ] Re-check the blob container URLs and the DAPR licence (the brief flags it as *check*)
- [ ] Run `make new-project`
- [ ] Add dependencies and install
- [ ] Seed `config.yaml` and `.env.example`
- [ ] Paste the headline questions and data table into the project README
- [ ] `make check`

## Acceptance criteria

- [ ] Project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import rail_delay_copilot"` works from the project folder
- [ ] `git check-ignore .env` confirms the key file is ignored
- [ ] `make check` passes
