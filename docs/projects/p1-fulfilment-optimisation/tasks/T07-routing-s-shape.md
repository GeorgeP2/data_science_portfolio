# T07: S-shape routing

**Phase:** 2 Routing · **Estimate:** 1 h · **Depends on:** T04

## Ask

Implement S-shape (traversal) routing: given a batch's pick locations, return the route and its length.

## Why

S-shape is the standard practitioner heuristic and one of the routing policies the published
batching results are reported under.

## How

- Enter every aisle containing a pick and traverse it fully; if the number of such aisles is odd,
  return from the last one. Follow the exact variant the benchmark papers use.
- Shared `Router` protocol: `route(locations, layout) -> Route`.

## Plan

- [ ] Define the `Router` protocol
- [ ] Implement S-shape
- [ ] Tests on hand-drawn cases (odd/even aisle counts, single pick, empty batch)

## Acceptance criteria

- [ ] Route length matches hand calculation on at least 4 test cases
- [ ] Empty batch returns length 0
- [ ] Route visits every pick location
