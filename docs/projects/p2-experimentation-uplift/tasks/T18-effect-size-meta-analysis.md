# T18: Effect-size meta-analysis and MDE guidance

**Phase:** 3 Sequential testing · **Estimate:** 2 h · **Depends on:** T13

## Ask

Estimate the distribution of true effect sizes across the ASOS experiments and turn it into guidance
on sensible minimum detectable effects.

## Why

Knowing what a typical e-commerce effect looks like tells you which MDEs are realistic, and gives a
data-driven prior for the mSPRT mixing variance (T15).

## How

- Final-checkpoint relative effects and SEs per experiment/metric.
- Random-effects meta-analysis (DerSimonian–Laird or REML) to separate true spread (tau) from noise.
- Report quantiles of the deconvolved effect distribution; translate into "an MDE of X% would catch
  Y% of real effects".

## Plan

- [ ] Extract effects and SEs
- [ ] Random-effects model
- [ ] Effect-size distribution chart
- [ ] MDE guidance table

## Acceptance criteria

- [ ] tau² and the pooled mean are reported with CIs
- [ ] MDE guidance table gives the share of effects detectable at ≥ 3 MDE levels
- [ ] The estimate feeds T15's default mixing variance
