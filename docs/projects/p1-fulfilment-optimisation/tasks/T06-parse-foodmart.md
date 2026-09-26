# T06: Parser for Foodmart instances

**Phase:** 1 Core model · **Estimate:** 1.5 h · **Depends on:** T03, T04

## Ask

Load the Arbex Valle et al. Foodmart instances (8/16-aisle layouts, 1,560 SKUs, 5–5,000 orders) into
`Instance`s.

## Why

A second external benchmark with larger instances and realistic SKU/order-size distributions. It
tests scaling and feeds the generator's validity check.

## How

- Same shape as T05. Map the SKU → location assignment into `Location`s.
- If the layout generator shipped with the instances uses a different geometry than T04 supports,
  note the gap and restrict to compatible layouts rather than extending scope.

## Plan

- [ ] Inspect the file format
- [ ] Write `load_foodmart(path) -> Instance`
- [ ] Fixture-based test
- [ ] Summary: instances by aisles and order count

## Acceptance criteria

- [ ] All in-scope instances parse; any excluded ones are listed with the reason
- [ ] SKU count is 1,560 and aisle counts are 8 or 16
- [ ] Fixture test passes without raw data
