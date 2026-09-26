# T04: Domain model and warehouse distance function

**Phase:** 1 Core model · **Estimate:** 2 h · **Depends on:** T01

## Ask

Define the core types (`Layout`, `Location`, `Order`, `Batch`, `Route`, `Instance`) and a distance
function for a single-block, parallel-aisle, picker-to-parts warehouse with one depot.

## Why

Parsers, generator, routers, solvers and the API all exchange these types. Getting them right once
avoids adapters everywhere, and a single distance function makes every solver's numbers comparable.

## How

- Frozen dataclasses (or pydantic models if the API can reuse them directly; decide here).
- Layout: number of aisles, locations per aisle, aisle width, cross-aisle positions, depot position,
  picker capacity.
- Location: aisle index + position along aisle (+ side if the benchmark distinguishes it).
- Distances follow the conventions of the published instances so gaps are comparable. Read the
  Henn & Wäscher paper to confirm units and depot placement.

## Plan

- [ ] Read the conventions in Henn & Wäscher (2012) and the Foodmart paper
- [ ] Write the types
- [ ] Write `distance(a, b, layout)` for within-aisle and cross-aisle moves
- [ ] Unit tests with hand-computed distances

## Acceptance criteria

- [ ] Types are importable and typed (mypy-clean)
- [ ] Distance tests cover: same aisle, adjacent aisles, depot to far corner, symmetry
- [ ] Units and depot conventions are documented in a docstring with the paper reference
