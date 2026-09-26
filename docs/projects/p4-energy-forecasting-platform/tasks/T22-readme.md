# T22: Project README

**Phase:** 5 Write-up · **Estimate:** 1.5 h · **Depends on:** T13, T16, T17, T20, T21

## Ask

Write the project README, leading with the result and including the calibration plots for both models.

## Why

"Done when" requires calibration plots for both models in the README, and the README is what most
readers will see.

## How

- Order: headline chart + three bullets answering both headline questions → architecture diagram
  (flow, MLflow, API, dashboard) → calibration plots → household comparison table + verdict → drift
  result → design decisions → reproduce → data and licences → limitations.
- Tick every item on the `docs/conventions.md` README checklist.

## Plan

- [ ] Headline chart and bullets
- [ ] Architecture diagram
- [ ] Remaining sections
- [ ] Follow the reproduce section from a clean clone (using the LCL development sample)

## Acceptance criteria

- [ ] National and household calibration plots are both in the README
- [ ] Every item on the conventions README checklist is present
- [ ] Reproduce section works from a clean clone
- [ ] MLflow run history from the scheduled runs is shown
