# T20 (stretch): Fairness constraint for low-usage households

**Phase:** Stretch · **Estimate:** 2 h · **Depends on:** T10, T11

## Ask

Add a constraint that caps bill increases for low-usage households, and measure what it costs in margin.

## Why

It makes the ethics discussion in T18 concrete, as a quantified trade-off.

## How

- Define "low-usage" (e.g. bottom usage quantile) and the bill-increase cap relative to a reference
  tariff, both in `config.yaml`.
- Add to the optimiser and the property tests; expose it as a toggle in the Streamlit app.
- Report the margin cost of the constraint across cap levels.

## Plan

- [ ] Only start once T01–T19 are done
- [ ] Constraint and definition
- [ ] Property test
- [ ] Margin-vs-cap chart

## Acceptance criteria

- [ ] Property test proves no low-usage bill increase exceeds the cap
- [ ] Chart of margin cost vs cap level is in `results/`
