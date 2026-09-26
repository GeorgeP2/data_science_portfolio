# T14: Benchmark harness

**Phase:** 4 Benchmarking · **Estimate:** 2 h · **Depends on:** T05, T09, T10

## Ask

Build a harness that runs every solver × router × instance × time limit and writes the results.

## Why

All headline numbers, the results table and the Pareto chart come from this. It must be reproducible
from one command.

## How

- Grid defined in `config.yaml` (solvers, routers, time limits, instance sets, seeds).
- One row per run: instance, solver, router, time limit, seed, distance, solve time, finished flag.
- Derived metrics: gap to best-known, % distance saved vs FCFS, p50/p95 solve time; summary written
  with `portfolio.evaluation` to `outputs/metrics.json`.
- Parallel across instances with `concurrent.futures`; one process per run so timings aren't shared.

## Plan

- [ ] Grid config
- [ ] Runner writing raw rows to `outputs/`
- [ ] Aggregation into metrics
- [ ] Smoke test on 2 instances × 2 solvers

## Acceptance criteria

- [ ] `PYTHONPATH=src python -m fulfilment_optimisation.benchmark` runs the full grid
- [ ] Re-running with the same config gives identical distances
- [ ] Output includes gap to best-known, % saved vs FCFS, p50 and p95 solve time
- [ ] Smoke test is part of `make check`
