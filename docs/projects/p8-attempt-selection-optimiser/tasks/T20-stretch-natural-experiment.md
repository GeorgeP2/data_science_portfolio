# T20 (stretch): Natural experiment around a federation rule change

**Phase:** Stretch · **Estimate:** 4 h · **Depends on:** T05

## Ask

Run a difference-in-differences or regression discontinuity analysis around a federation rule change,
e.g. a weight-class restructure.

## Why

Adds a causal-inference angle and links to Project 2.

## How

- First verify a specific rule change, its date and which federations it affected (the brief says
  this needs verifying).
- Choose DiD (affected vs unaffected federations) or RD (around the date) based on what the change allows.
- Candidate outcomes: jump sizes, make rates, totals. Aggregate only.

## Plan

- [ ] Only start once T01–T19 are done
- [ ] Verify and document the rule change with a source
- [ ] Choose the design; check pre-trends or continuity
- [ ] Estimate and write up

## Acceptance criteria

- [ ] Rule change cited with a source
- [ ] Identification assumptions checked (pre-trend plot or density test)
- [ ] Effect estimate with confidence interval and limitations written up in `results/`
