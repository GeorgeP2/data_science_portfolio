# T16: Distance-saved vs solve-time Pareto chart

**Phase:** 4 Benchmarking · **Estimate:** 1 h · **Depends on:** T14

## Ask

Plot distance saved vs FCFS against solve-time budget, one curve per solver, on the published instances.

## Why

This is the headline chart and answers the second half of the headline question: what each extra
millisecond buys.

## How

- x: time budget (log scale), y: mean % distance saved vs FCFS, with an uncertainty band across
  instances. Mark the Pareto frontier.
- Save with `portfolio.plotting.save_fig` to `reports/figures/`.

## Plan

- [ ] Add enough time-limit points to the harness grid for smooth curves
- [ ] Plot
- [ ] Check readability at README width

## Acceptance criteria

- [ ] Figure is in `reports/figures/` and regenerates from harness output
- [ ] Every solver has a curve; axes labelled with units
- [ ] The frontier is identifiable at a glance
