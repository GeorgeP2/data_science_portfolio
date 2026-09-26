# T06: Schema description for text-to-SQL

**Phase:** 1 Ingestion · **Estimate:** 1 h · **Depends on:** T05

## Ask

Write the schema description the LLM sees: views, columns, meanings, units, join keys, and the
gotchas (dedup, deemed minutes, data ending Dec 2023).

## Why

Text-to-SQL accuracy depends mostly on schema context, and the domain gotchas are exactly where a
naive query goes wrong.

## How

- A YAML file generated partly from DuckDB metadata, with hand-written descriptions.
- A few example question → SQL pairs, none taken from the golden set.

## Plan

- [ ] Generate the column list from DuckDB
- [ ] Write descriptions and gotchas
- [ ] Add 5–10 example pairs

## Acceptance criteria

- [ ] Every column exposed to the agent has a description, with units where relevant
- [ ] Gotchas cover dedup, deemed minutes and the data end date
- [ ] A test fails if a view gains a column without a description
