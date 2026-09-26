# T11: Seed and savings batching heuristics

**Phase:** 3 Solvers · **Estimate:** 2 h · **Depends on:** T10

## Ask

Implement a seed heuristic and a Clarke & Wright savings heuristic for order batching.

## Why

These are the classic constructive heuristics in the batching literature (de Koster et al., 1999).
They're a stronger baseline than FCFS and a good starting solution for local search.

## How

- Seed: pick a seed order by a rule (e.g. most aisles), then add the order that fits and is closest by
  a similarity rule, until capacity is reached.
- Savings: start from single-order batches, merge the pair with the largest distance saving that
  stays within capacity; recompute or approximate savings (state which).

## Plan

- [ ] Implement seed with one seed rule and one addition rule (configurable in `config.yaml`)
- [ ] Implement savings
- [ ] Tests on a small instance with a known answer

## Acceptance criteria

- [ ] Both pass the feasibility checker on all Henn & Wäscher instances
- [ ] Both beat FCFS on average total distance across those instances
- [ ] Chosen rule variants are named and cited in docstrings
