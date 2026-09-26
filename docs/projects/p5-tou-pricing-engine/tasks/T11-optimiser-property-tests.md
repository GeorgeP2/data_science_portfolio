# T11: Property-based tests for the optimiser

**Phase:** 3 Optimiser · **Estimate:** 1.5 h · **Depends on:** T10

## Ask

Use Hypothesis to show that every schedule the optimiser returns respects every constraint.

## Why

"Done when" requires property-based tests showing the optimiser respects every constraint. The
Streamlit app lets users move constraints freely, so edge cases will be hit.

## How

- Generate random costs, elasticities and constraint settings, including tight and conflicting ones.
- Properties: price ≤ cap everywhere, |step| ≤ max step and margin ≥ floor; otherwise the status is
  infeasible.
- Also: relaxing a constraint never lowers the optimal margin.

## Plan

- [ ] Input strategies
- [ ] Constraint properties
- [ ] Monotonicity property
- [ ] Add to `make check` with a bounded example count

## Acceptance criteria

- [ ] All properties pass on ≥ 500 generated cases
- [ ] Tests run in `make check` in under 60 s
- [ ] Any shrunk failing example found during development is kept as a regression test
