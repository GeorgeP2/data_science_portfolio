# T05: Household hierarchy for LCL

**Phase:** 1 Data · **Estimate:** 2 h · **Depends on:** T04

## Ask

Define the household → group → global hierarchy for the Bayesian model.

## Why

Partial pooling needs meaningful groups. The brief flags that ACORN socio-demographic groups may only
be in the refactored 4TU copy of LCL.

## How

- Confirm whether ACORN groups are in the London Datastore copy. If not, check the 4TU copy.
- Fallback: tariff group (Std/ToU) plus k-means clustering on normalised average daily load shape,
  fitted on pre-2013 data only so the ToU trial doesn't leak into the grouping.
- Save a `household_id → group` table to `data/processed/`.

## Plan

- [ ] Check both LCL copies for ACORN
- [ ] If absent, implement load-shape clustering; choose k by silhouette score or similar
- [ ] Write the mapping table
- [ ] Record the choice and group sizes

## Acceptance criteria

- [ ] Every household has exactly one group
- [ ] Group sizes are reported, including which groups are sparse
- [ ] The hierarchy source (ACORN or fallback) is documented with the reason
