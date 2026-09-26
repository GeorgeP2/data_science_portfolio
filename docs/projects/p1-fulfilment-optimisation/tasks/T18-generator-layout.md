# T18: Generator: layout

**Phase:** 5 Generator · **Estimate:** 1 h · **Depends on:** T04, T17

## Ask

Implement `layout`: generate a `Layout` from parameters (aisles, locations per aisle, depot, capacity)
sampled within the ranges from T17.

## Why

The first generator component; the others place SKUs and orders onto it.

## How

- Pure function of parameters + seed. Parameter ranges live in `config.yaml`, populated from T17.

## Plan

- [ ] Implement
- [ ] Tests: determinism, parameters within range, compatible with routers

## Acceptance criteria

- [ ] Same seed produces the same layout
- [ ] Generated layouts route without error under all three routers
- [ ] Default ranges in `config.yaml` cite the T17 output
