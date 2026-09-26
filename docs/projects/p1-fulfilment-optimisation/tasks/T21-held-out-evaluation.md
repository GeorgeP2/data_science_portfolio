# T21: Held-out generated set and final numbers

**Phase:** 5 Generator · **Estimate:** 1 h · **Depends on:** T14, T19

## Ask

Freeze a held-out set of generated instances (fixed seeds, all scenarios) and run the final benchmark
on it after all solver tuning is done.

## Why

It's easy to over-tune on 96 instances. Final claims need data the solvers weren't tuned on.

## How

- Seeds for the held-out set live in `config.yaml` and are not used during development.
- Tuning uses a separate development seed range.
- Run once, at the end; report next to the published-instance results.

## Plan

- [ ] Reserve seed ranges (dev vs held-out)
- [ ] Freeze solver parameters
- [ ] Run the harness on the held-out set
- [ ] Add results to the results table

## Acceptance criteria

- [ ] Held-out seeds are documented and disjoint from dev seeds
- [ ] Solver config used for the final run is committed before the run
- [ ] Results table shows held-out numbers per scenario
