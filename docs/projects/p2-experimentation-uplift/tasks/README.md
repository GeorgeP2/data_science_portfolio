# P2 tasks

Atomic tasks for [Experimentation & Uplift](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-download-scripts.md) | Download GGL + ASOS | 0 Setup | 1 h | T01 |
| [T03](T03-ggl-load-and-clean.md) | Load and clean GGL | 1 Field experiment basics | 1.5 h | T02 |
| [T04](T04-srm-and-balance.md) | SRM and covariate balance | 1 Field experiment basics | 1.5 h | T03 |
| [T05](T05-ate-clustered-se.md) | ATE with clustered SEs | 1 Field experiment basics | 2 h | T03 |
| [T06](T06-cuped-regression-adjustment.md) | CUPED / regression adjustment | 1 Field experiment basics | 2 h | T05 |
| [T07](T07-leakage-safe-features.md) | Leakage-safe features | 2 Heterogeneous effects | 1.5 h | T03 |
| [T08](T08-t-and-x-learners.md) | T- and X-learners | 2 Heterogeneous effects | 2 h | T07 |
| [T09](T09-causal-forest-and-dr-learner.md) | Causal forest + DR-learner | 2 Heterogeneous effects | 2 h | T07 |
| [T10](T10-qini-and-targeting.md) | Qini curves + budget targeting | 2 Heterogeneous effects | 2.5 h | T08, T09 |
| [T11](T11-lenta-stress-test.md) | Lenta stress test | 2 Heterogeneous effects | 2 h | T10 |
| [T12](T12-power-calculator.md) | Power calculator | 2 Heterogeneous effects | 2.5 h | T05, T06 |
| [T13](T13-asos-load.md) | Load and validate ASOS | 3 Sequential testing | 1 h | T02 |
| [T14](T14-peeking-simulation.md) | Peeking simulation | 3 Sequential testing | 2 h | T13 |
| [T15](T15-msprt-confidence-sequences.md) | mSPRT + confidence sequences | 3 Sequential testing | 3 h | T14 |
| [T16](T16-group-sequential-obf.md) | Group-sequential (O'Brien–Fleming) | 3 Sequential testing | 2 h | T14 |
| [T17](T17-time-to-decision.md) | Time-to-decision across experiments | 3 Sequential testing | 2 h | T15, T16 |
| [T18](T18-effect-size-meta-analysis.md) | Effect-size meta-analysis + MDEs | 3 Sequential testing | 2 h | T13 |
| [T19](T19-make-analysis-pipeline.md) | `make analysis` pipeline | 4 Pipeline and write-up | 1.5 h | T04–T06, T10, T12, T17, T18 |
| [T20](T20-decision-memo.md) | Decision memo | 4 Pipeline and write-up | 2.5 h | T10, T17, T19 |
| [T21](T21-design-decisions-writeup.md) | Design decisions write-up | 4 Pipeline and write-up | 2 h | T05, T06, T10, T17 |
| [T22](T22-readme.md) | Project README | 4 Pipeline and write-up | 1.5 h | T10, T12, T17, T20, T21 |
| [T23](T23-stretch-bayesian-ab.md) | *Stretch:* Bayesian A/B (PyMC) | Stretch | 3 h | T05 |
| [T24](T24-stretch-did-synthetic-control.md) | *Stretch:* DiD / synthetic control | Stretch | 4 h | T01 |

**Total:** ~41 h must-have against a ~40 h time box. If it runs over, cut in this order: T11 (Lenta
stress test), then the Streamlit front end in T12 (keep the CLI), then the DR-learner in T09.

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| Notebook-free reproducible pipeline: `make analysis` → figures + memo | T19 |
| Qini chart and sequential-testing chart in the README | T10, T17, T22 |
| Power calculator usable by someone else | T12 |
| Decision memo in `reports/` | T20 |
