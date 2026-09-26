# T15: Monitor and one-command stack

**Phase:** 3 Streaming · **Estimate:** 2 h · **Depends on:** T12

## Ask

Add a small monitor (Grafana or Streamlit) showing live throughput, decision rate and latency, and
make `make up && make replay` bring up the whole stack.

## Why

"`make up && make replay` shows live scoring with a latency panel" is a "done when" item.

## How

- Pick the lighter option: Streamlit reading the `decisions` topic, or Prometheus metrics from the
  scorer + Grafana with a provisioned dashboard. Record the choice.
- Panels: transactions/s, decline rate, p50/p99 end-to-end latency, per-stage latency breakdown.
- `make up` starts Redpanda + (Redis) + scorer + monitor; `make down` tears it down.

## Plan

- [ ] Choose monitor
- [ ] Expose metrics from the scorer
- [ ] Dashboard/app with the panels
- [ ] `make up` / `make down` targets
- [ ] Screenshot for the README

## Acceptance criteria

- [ ] From a clean clone with data downloaded, `make up && make replay` shows live scoring with a latency panel
- [ ] Latency panel shows p50 and p99
- [ ] Screenshot saved to `reports/figures/`
