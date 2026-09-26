# T19: Streamlit dashboard

**Phase:** 4 Platform · **Estimate:** 2 h · **Depends on:** T10, T13, T17, T18

## Ask

Build a Streamlit dashboard with a forecast fan chart, a calibration plot and the drift status.

## Why

It's the visible front of the platform and the cheapest way to host a live demo.

## How

- Page 1: next-day fan chart (from `/forecast`) with recent actuals.
- Page 2: calibration plots for both models.
- Page 3: drift status for the national flow, plus the LCL 2013 replay timeline.
- Read precomputed artefacts where possible so the dashboard stays fast.

## Plan

- [ ] Fan chart page
- [ ] Calibration page
- [ ] Drift page
- [ ] Run locally against the API

## Acceptance criteria

- [ ] All three views render from a single `streamlit run` command
- [ ] Fan chart shows at least the 50% and 90% intervals
- [ ] Dashboard handles the API being unavailable with a clear message
