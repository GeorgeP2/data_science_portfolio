# P4 tasks

Atomic tasks for the [Energy Demand Forecasting Platform](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-neso-ingestion.md) | NESO demand ingestion | 1 Data | 2 h | T01 |
| [T03](T03-settlement-periods.md) | Settlement periods + clock changes (shared) | 1 Data | 1.5 h | T01 |
| [T04](T04-lcl-to-parquet.md) | LCL download → Parquet (shared) | 1 Data | 2 h | T01 |
| [T05](T05-lcl-hierarchy.md) | LCL household hierarchy | 1 Data | 2 h | T04 |
| [T06](T06-weather-cache.md) | Open-Meteo weather + cache | 1 Data | 1.5 h | T01 |
| [T07](T07-data-quality-checks.md) | Data-quality checks (Pandera) | 1 Data | 1.5 h | T02, T03, T04, T06 |
| [T08](T08-backtest-framework.md) | Rolling backtest + metrics | 2 National model | 2 h | T02, T03 |
| [T09](T09-national-point-models.md) | Seasonal naive + LightGBM | 2 National model | 2 h | T06, T07, T08 |
| [T10](T10-quantile-conformal.md) | Quantile LightGBM + conformal | 2 National model | 2.5 h | T09 |
| [T11](T11-household-lightgbm-baselines.md) | Household LightGBM baselines | 3 Household model | 2 h | T05, T06, T08 |
| [T12](T12-pymc-hierarchical-model.md) | PyMC hierarchical model | 3 Household model | 4 h | T05, T11 |
| [T13](T13-household-comparison.md) | Household comparison + verdict | 3 Household model | 2 h | T11, T12 |
| [T14](T14-mlflow-tracking-registry.md) | MLflow tracking + registry | 4 Platform | 1.5 h | T10 |
| [T15](T15-prefect-flow-promotion.md) | Prefect flow + promotion gate | 4 Platform | 2.5 h | T02, T07, T10, T14 |
| [T16](T16-daily-schedule.md) | Scheduled daily run | 4 Platform | 1.5 h | T15 |
| [T17](T17-drift-reports.md) | Evidently drift + 2013 ToU replay | 4 Platform | 2.5 h | T04, T05, T07 |
| [T18](T18-forecast-api.md) | FastAPI `/forecast` | 4 Platform | 1.5 h | T14 |
| [T19](T19-streamlit-dashboard.md) | Streamlit dashboard | 4 Platform | 2 h | T10, T13, T17, T18 |
| [T20](T20-dockerfile.md) | Dockerfile + local run | 4 Platform | 1 h | T18, T19 |
| [T21](T21-design-decisions-writeup.md) | Design decisions write-up | 5 Write-up | 2 h | T10, T13, T15 |
| [T22](T22-readme.md) | Project README | 5 Write-up | 1.5 h | T13, T16, T17, T20, T21 |
| [T23](T23-stretch-terraform-cloud-run.md) | *Stretch:* Terraform for Cloud Run + scheduled job | Stretch | 3 h | T16, T20 |
| [T24](T24-stretch-reconciliation-check.md) | *Stretch:* Hierarchical reconciliation check | Stretch | 2 h | T12 |

**Total:** ~42 h must-have against a ~35 h time box. If it runs over, cut in this order: T05's
load-shape clustering (use tariff group alone as the hierarchy), then the per-household LightGBM in
T11 (keep the pooled one), then T19 down to the fan chart and calibration views.

T16 also needs about a week of elapsed time for the daily runs to build up, so start it early in the
platform phase.

**Shared code:** Project 5 reuses LCL and GB half-hourly conventions, so the settlement-period
utility (T03) and the LCL loader (T04) go in `src/portfolio/`, not the project package.

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| Scheduled daily run on NESO data with MLflow history visible | T14, T15, T16 |
| Calibration plots for both models in the README | T10, T13, T22 |
| Drift report showing the 2013 ToU trial detected | T17 |
| Hierarchical vs LightGBM comparison table, with an honest verdict | T11, T12, T13 |
