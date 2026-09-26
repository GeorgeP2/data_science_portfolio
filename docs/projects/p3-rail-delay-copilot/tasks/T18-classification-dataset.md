# T18: Incident classification dataset

**Phase:** 5 Fine-tune vs prompt · **Estimate:** 1.5 h · **Depends on:** T05

## Ask

Build the dataset: `INCIDENT_DESCRIPTION` + event type + location → `INCIDENT_REASON`, restricted to
the top ~30 codes plus "other", with train / validation / test splits.

## Why

All three approaches in the experiment must be scored on identical data. Restricting to the top
codes handles the class imbalance across 212 codes.

## How

- One row per deduplicated incident (T05) so repeated rows don't leak across splits.
- Time-based split (e.g. latest periods as test) to mimic real use; state the choice.
- Report class distribution and the share of incidents covered by the top 30.

## Plan

- [ ] Select top-N codes (N in config)
- [ ] Build rows from the `incidents` view
- [ ] Time-based splits
- [ ] Save to `data/processed/` and summarise

## Acceptance criteria

- [ ] No `INCIDENT_NUMBER` appears in more than one split
- [ ] Class distribution and top-30 coverage are reported
- [ ] A fixed, smaller test subset is defined for the paid API evaluation
