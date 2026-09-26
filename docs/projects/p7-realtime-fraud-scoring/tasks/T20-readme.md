# T20: Project README

**Phase:** 5 Write-up · **Estimate:** 1.5 h · **Depends on:** T08, T10, T15, T16, T18, T19

## Ask

Write the project README, leading with the result.

## Why

"Cost curve + chosen threshold in the README" and "fairness companion section" are "done when" items,
and the README is what most readers will see.

## How

- Order: cost curve + three bullets (net saving at the SLO, what stateful features add, latency) →
  architecture diagram → ablation table → latency results → fairness companion with the group table →
  design decisions → reproduce → data and licences → limitations (synthetic data up front).
- Tick every item on the `docs/conventions.md` README checklist.

## Plan

- [ ] Headline chart and bullets
- [ ] Architecture diagram
- [ ] Remaining sections
- [ ] Follow the reproduce section from a clean clone

## Acceptance criteria

- [ ] README contains the cost curve with the chosen threshold
- [ ] Fairness companion section includes the group metrics table
- [ ] TabFormer is clearly labelled synthetic
- [ ] Every item on the conventions README checklist is present
- [ ] Reproduce section works from a clean clone
