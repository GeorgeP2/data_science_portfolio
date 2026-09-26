# T08: Largest-gap routing

**Phase:** 2 Routing · **Estimate:** 1 h · **Depends on:** T07

## Ask

Implement largest-gap routing behind the same `Router` protocol.

## Why

The second standard heuristic in the literature. It is usually shorter than S-shape at low pick
density, which is part of the routing story.

## How

- Traverse the first and last pick aisles fully; in the others, enter from front and back up to the
  largest gap between adjacent picks (including the aisle ends).

## Plan

- [ ] Implement largest-gap
- [ ] Tests on hand-drawn cases
- [ ] Property test: never longer than S-shape by more than the definition allows on random batches

## Acceptance criteria

- [ ] Matches hand calculation on at least 4 cases
- [ ] Visits every pick location
- [ ] Property test runs on ≥ 1,000 random batches
