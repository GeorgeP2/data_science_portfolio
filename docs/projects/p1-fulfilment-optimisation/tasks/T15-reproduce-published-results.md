# T15: Reproduce published results

**Phase:** 4 Benchmarking · **Estimate:** 2 h · **Depends on:** T03, T11, T12, T13, T14

## Ask

Produce the results table comparing my solvers against the published best-known values, with a
stated tolerance.

## Why

"Done when" requires the table to reproduce published results. It is the credibility claim that lets
a reader trust the rest.

## How

- First reproduce a published *heuristic* result (e.g. savings + S-shape) to confirm the parser,
  distances and router match the paper. Only then compare improved solvers to best-known.
- Choose and state the tolerance (e.g. within 1% of the published heuristic value) before looking at
  the final numbers.
- Table grouped by instance class (orders, capacity, routing).

## Plan

- [ ] Set tolerance in writing
- [ ] Reproduce one published heuristic result per instance class
- [ ] Investigate and explain any class outside tolerance
- [ ] Generate the table into `docs/projects/p1-fulfilment-optimisation/results/`

## Acceptance criteria

- [ ] Tolerance is written down and justified
- [ ] Published heuristic results are reproduced within tolerance, or each miss is explained
- [ ] Table shows, per class: best-known, each solver's value, gap %
- [ ] Table regenerates from the harness output with one command
