# T10: Text-to-SQL tool with validation

**Phase:** 3 Agent · **Estimate:** 3 h · **Depends on:** T06

## Ask

Implement `query_delays`: question → SQL → validation → read-only, row-limited execution → result.

## Why

The operational half of the copilot. Validating before execution is what makes letting an LLM write
SQL safe.

## How

- LLM generates SQL from the T06 schema description.
- Validate with `sqlglot`: a single `SELECT`, only known tables/columns, `LIMIT` enforced.
- Execute on a read-only DuckDB connection with a timeout; one retry passing the error back on failure.
- Return SQL, rows and a short answer.

## Plan

- [ ] Generation prompt
- [ ] Validator
- [ ] Read-only execution with limits and timeout
- [ ] Retry on error
- [ ] Validator tests (no LLM needed)

## Acceptance criteria

- [ ] Validator rejects `INSERT`/`UPDATE`/`DELETE`/`DROP`/`ATTACH`, multiple statements and unknown tables
- [ ] Connection is read-only: a write fails even if validation is bypassed
- [ ] Results never exceed the configured row limit
- [ ] Validator tests run in CI without an API key
