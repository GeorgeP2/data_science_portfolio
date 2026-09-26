# T09: Optimal routing (Ratliff & Rosenthal)

**Phase:** 2 Routing · **Estimate:** 3 h · **Depends on:** T07

## Ask

Implement exact routing for a single-block parallel-aisle warehouse using the Ratliff & Rosenthal
(1983) dynamic programme.

## Why

Optimal routing is the lower bound for routing and shows how much the heuristics leave on the table.
It's also the algorithm most readers won't have seen implemented.

## How

- The DP over aisles with the 7 aisle-transition types and connectivity states from the paper.
- Validate against brute force (TSP over pick locations with the T04 distance) on small batches.

## Plan

- [ ] Re-read the paper and write the state/transition table as a comment
- [ ] Implement the DP
- [ ] Brute-force validator for batches of ≤ 8 picks
- [ ] Randomised comparison test

## Acceptance criteria

- [ ] Equals brute force on ≥ 500 random small batches
- [ ] Never longer than S-shape or largest-gap on ≥ 1,000 random batches
- [ ] Runs in under 10 ms for a 100-pick batch on a 10-aisle layout
