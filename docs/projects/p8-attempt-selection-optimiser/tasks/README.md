# P8 tasks

Atomic tasks for the [Powerlifting Attempt Selection Optimiser](../brief.md). One file per task, each
with **Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-download-openpowerlifting.md) | Download OpenPowerlifting bulk CSV | 0 Setup | 1 h | T01 |
| [T03](T03-attempt-coverage-filter.md) | Filter to full-attempt meets + coverage | 1 Data preparation | 2 h | T02 |
| [T04](T04-clean-entries.md) | Clean entries | 1 Data preparation | 2 h | T03 |
| [T05](T05-attempt-table-and-split.md) | Attempt table, features, time split | 1 Data preparation | 2 h | T04 |
| [T06](T06-eval-harness-and-logistic-baseline.md) | Evaluation harness + logistic baseline | 2 Make-probability model | 2 h | T05 |
| [T07](T07-lightgbm-comparison.md) | LightGBM comparison | 2 Make-probability model | 1 h | T06 |
| [T08](T08-bayesian-model-spec.md) | Bayesian model: specification | 2 Make-probability model | 3 h | T05 |
| [T09](T09-bayesian-fit-and-evaluate.md) | Bayesian model: fit at scale + evaluate | 2 Make-probability model | 3 h | T06, T08 |
| [T10](T10-make-probability-interface.md) | Make-probability interface | 2 Make-probability model | 1 h | T09 |
| [T11](T11-dp-optimiser-expected-total.md) | DP optimiser: expected total | 3 Optimiser | 3 h | T10 |
| [T12](T12-property-tests-federation-rules.md) | Property tests for federation rules | 3 Optimiser | 1.5 h | T11 |
| [T13](T13-objective-target-total.md) | Objective: P(total ≥ target) | 3 Optimiser | 1 h | T11 |
| [T14](T14-objective-expected-placing.md) | Objective: expected placing | 3 Optimiser | 2.5 h | T11, T13 |
| [T15](T15-retrospective-analysis.md) | Retrospective: total left on the table | 4 Analysis | 3 h | T09, T11 |
| [T16](T16-demo-app.md) | Demo app | 5 Demo | 2.5 h | T10, T13, T14 |
| [T17](T17-deploy-demo.md) | Deploy the demo | 5 Demo | 1 h | T16 |
| [T18](T18-design-decisions-writeup.md) | Design decisions write-up | 6 Write-up | 2 h | T07, T09, T14, T15 |
| [T19](T19-readme.md) | Project README | 6 Write-up | 1.5 h | T09, T15, T17, T18 |
| [T20](T20-stretch-natural-experiment.md) | *Stretch:* natural experiment | Stretch | 4 h | T05 |
| [T21](T21-stretch-live-updating.md) | *Stretch:* live plan updating | Stretch | 2 h | T16 |

**Total:** ~36 h must-have against a ~30 h time box. If it runs over, cut in this order: T07
(LightGBM; use the logistic baseline as the only comparison), then simplify T14's field to a single
fitted distribution per group, then run T09 on a subsample rather than the full data.

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| Calibration plot of make probability on held-out future meets in the README | T05, T06, T09, T19 |
| "Total left on the table" chart, by attempt and by lift | T15 |
| Optimiser respects federation rules, with property-based tests to prove it | T11, T12 |
| Live demo with OpenPowerlifting credited | T16, T17 |
