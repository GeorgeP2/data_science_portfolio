# T20: Generator validity check

**Phase:** 5 Generator · **Estimate:** 2 h · **Depends on:** T05, T06, T19

## Ask

Show that generated instances resemble the benchmarks by comparing key distributions.

## Why

The brief lists generator validity as a design decision to write up. Without evidence, results on
generated instances don't transfer.

## How

- Compare order size, aisles visited per order and per batch, and SKU popularity skew between
  generated instances and KIT / Foodmart / Henn & Wäscher.
- Two-sample KS or Wasserstein distance plus overlaid plots; also check that solver *rankings* agree
  on generated vs published instances.

## Plan

- [ ] Choose statistics and thresholds up front
- [ ] Compute comparisons
- [ ] Plots into `reports/figures/`
- [ ] Short write-up in `results/`

## Acceptance criteria

- [ ] At least 3 distributions compared, with a numeric distance and a plot each
- [ ] Solver ranking on generated instances is reported alongside the ranking on published ones
- [ ] Any mismatch is stated, not hidden
