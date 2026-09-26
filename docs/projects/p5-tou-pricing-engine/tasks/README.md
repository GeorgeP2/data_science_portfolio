# P5 tasks

Atomic tasks for the [Time-of-Use Pricing Engine](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-octopus-agile-history.md) | Download and stitch Agile history | 0 Setup | 3 h | T01 |
| [T03](T03-lcl-and-weather-loaders.md) | LCL + weather loaders (shared with P4) | 0 Setup | 2 h | T01 |
| [T04](T04-open-bandit-download.md) | Download Open Bandit | 0 Setup | 1 h | T01 |
| [T05](T05-lcl-trial-design.md) | Confirm LCL trial assignment | 1 Elasticity | 1 h | none |
| [T06](T06-elasticity-dataset.md) | Elasticity modelling dataset | 1 Elasticity | 2 h | T03, T05 |
| [T07](T07-elasticity-model.md) | Estimate elasticities | 1 Elasticity | 3 h | T06 |
| [T08](T08-simulator-baseline-and-costs.md) | Simulator: baseline demand + costs | 2 Simulator | 2 h | T02, T03 |
| [T09](T09-simulator-price-response.md) | Simulator: price response | 2 Simulator | 2 h | T07, T08 |
| [T10](T10-constrained-optimiser.md) | Constrained schedule optimiser | 3 Optimiser | 3 h | T09 |
| [T11](T11-optimiser-property-tests.md) | Optimiser property tests | 3 Optimiser | 1.5 h | T10 |
| [T12](T12-thompson-sampling-bandit.md) | Thompson-sampling bandit | 4 Bandit | 2.5 h | T09 |
| [T13](T13-regret-experiment.md) | Regret experiment + curve | 4 Bandit | 1.5 h | T10, T12 |
| [T14](T14-ope-estimators.md) | IPS / SNIPS / DR estimators | 5 OPE | 2 h | T01 |
| [T15](T15-ope-validation-open-bandit.md) | Validate OPE on Open Bandit | 5 OPE | 2 h | T04, T14 |
| [T16](T16-ope-on-simulator-logs.md) | OPE on simulator logs | 5 OPE | 1.5 h | T12, T14 |
| [T17](T17-streamlit-app.md) | Streamlit app | 6 App and write-up | 2 h | T10, T11 |
| [T18](T18-design-decisions-writeup.md) | Design decisions write-up | 6 App and write-up | 1.5 h | T05, T13, T16 |
| [T19](T19-readme.md) | Project README | 6 App and write-up | 1.5 h | T13, T15, T17, T18 |
| [T20](T20-stretch-fairness-constraint.md) | *Stretch:* fairness constraint | Stretch | 2 h | T10, T11 |
| [T21](T21-stretch-fuel-finder-collector.md) | *Stretch:* Fuel Finder snapshot collector | Stretch | 2 h | T01 |
| [T22](T22-stretch-competitor-response.md) | *Stretch:* competitor-response model | Stretch | 4 h | T21 |

**Total:** ~36 h must-have against a ~30 h time box. If it runs over, cut in this order:
1. T07: use the regression fallback instead of the hierarchical model (the brief allows it; ~1.5 h).
2. T03: if Project 4 has already built the shared loaders, this shrinks to ~0.5 h.
3. T16: drop the deliberate failure case and report one target policy.

**Start early:** if the Fuel Finder extension is wanted, run T21 at the start of the project, since it
needs weeks of snapshots before T22 is possible.

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| Regret curve (bandit vs oracle vs static tariff) in the README | T10, T12, T13, T19 |
| OPE validation table on Open Bandit (estimated vs actual) | T04, T14, T15 |
| Optimiser respects every constraint, with property-based tests | T10, T11 |
| Interactive Streamlit: move constraints, see schedule and margin change | T17 |
