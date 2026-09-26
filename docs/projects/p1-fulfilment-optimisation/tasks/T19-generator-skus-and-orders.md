# T19: Generator: SKU affinity and order arrivals

**Phase:** 5 Generator · **Estimate:** 2 h · **Depends on:** T18

## Ask

Implement `sku_affinity` (SKU popularity, co-purchase structure, storage assignment) and
`order_arrivals` (arrival times, lines per order, due dates).

## Why

These are what make generated scenarios realistic, and what enables peak-day, affinity and
tight-due-date stress scenarios that fixed benchmarks can't provide.

## How

- Popularity: skewed (e.g. Zipf-like) distribution; affinity via SKU clusters that co-occur in orders.
- Storage policy (random / class-based) from the KIT policies.
- Arrivals: non-homogeneous Poisson over a shift; lines per order and due-date slack from T17 fits.
- Named scenario presets in `config.yaml`: `baseline`, `peak_day`, `high_affinity`, `tight_due_dates`.

## Plan

- [ ] `sku_affinity`
- [ ] `order_arrivals`
- [ ] `generate_instance(scenario, seed) -> Instance`
- [ ] Scenario presets
- [ ] Tests

## Acceptance criteria

- [ ] `generate_instance` is deterministic per seed
- [ ] Generated instances pass the solver feasibility checker with every solver
- [ ] Each preset produces measurably different order statistics (e.g. peak_day has more orders/hour)
