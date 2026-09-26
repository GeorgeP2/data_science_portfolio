# T22 (stretch): Fuel Finder competitor-response model

**Phase:** Stretch · **Estimate:** 4 h · **Depends on:** T21

## Ask

Model how nearby stations react to a station's price change, using spatial neighbours and timestamped
updates.

## Why

Competitor response is what the core project leaves out: it treats demand response as the only
reaction to price.

## How

- Build station neighbour sets by distance.
- Event study: after a station changes price, measure the probability and size of neighbours' changes
  over the next hours, compared with a baseline window.
- Keep it descriptive unless the data supports more.

## Plan

- [ ] Only start once T01–T19 are done and T21 has ≥ a few weeks of data
- [ ] Neighbour graph
- [ ] Event-study analysis
- [ ] Chart and short write-up

## Acceptance criteria

- [ ] Response curve (neighbour change probability vs hours since change) with uncertainty
- [ ] Baseline comparison shows whether the response is above background change rates
- [ ] Findings summarised in `results/`
