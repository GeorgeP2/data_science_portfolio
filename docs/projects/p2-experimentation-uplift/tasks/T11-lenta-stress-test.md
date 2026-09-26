# T11: Lenta stress test for richer features

**Phase:** 2 Heterogeneous effects · **Estimate:** 2 h · **Depends on:** T10

## Ask

Rerun the uplift pipeline on Lenta (~687k customers, 190+ features; confirm) to show what richer
features do to the Qini curve.

## Why

The brief suggests Lenta to show that GGL's modest uplift comes from its few features, not the method.

## How

- Reuse T07–T10 code unchanged apart from the feature config.
- Licence is *unverified*: internal comparison only. Commit no data or per-row outputs, and confirm
  the licence before publishing even a summary chart.

## Plan

- [ ] Check licence status
- [ ] Lenta feature config
- [ ] Run learners + Qini
- [ ] Qini coefficients side by side: GGL vs Lenta

## Acceptance criteria

- [ ] Pipeline runs on Lenta with config changes only
- [ ] Qini coefficient comparison table exists
- [ ] Nothing derived from Lenta is published unless the licence is confirmed
