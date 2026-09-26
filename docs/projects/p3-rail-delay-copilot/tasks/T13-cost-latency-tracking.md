# T13: Cost and latency tracking dashboard

**Phase:** 3 Agent · **Estimate:** 2 h · **Depends on:** T11

## Ask

Record cost and latency for every query and show them in a small dashboard.

## Why

Required by the brief. The eval tables and the fine-tune comparison need the same numbers.

## How

- From each trace: input/output tokens × per-model price (prices in config with the date they were
  checked), end-to-end latency, per-tool latency.
- Append to a parquet/DuckDB log; a small Streamlit page with p50/p95 latency and cost per query by
  question type.

## Plan

- [ ] Cost calculation from token usage
- [ ] Query log
- [ ] Dashboard
- [ ] Test for the cost calculation

## Acceptance criteria

- [ ] Every agent run writes cost and latency to the log
- [ ] Dashboard shows p50/p95 latency and mean cost per query, by question type
- [ ] Prices live in config with a checked-on date
