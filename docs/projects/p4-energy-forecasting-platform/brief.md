# Project 4: Energy Demand Forecasting Platform with MLOps

**One line:** probabilistic electricity demand forecasting at two levels. A live GB national model
retrains daily on fresh NESO data. A hierarchical Bayesian household model on London smart meters
uses partial pooling across household groups. Both are tracked, monitored and served.

**Time box:** weeks 19–23 (~35 h). Reuses data with Project 6.

## Headline questions

> 1. How well can next-day GB demand be forecast, and are the prediction intervals **calibrated**
>    (does a 90% interval actually contain 90% of outcomes)?
> 2. For individual households with sparse or noisy history, does a hierarchical Bayesian model
>    (partial pooling across household groups) beat per-household or one-size-fits-all LightGBM
>    on accuracy and interval calibration?

## Why this data is different

- **M5 Walmart** is the default and is used everywhere. GB demand is UK-relevant.
- **Live data:** NESO data **updates continuously**, so "daily retraining" is real, not simulated.
- **Low Carbon London** (5,567 households, half-hourly, 2011–2014) is a natural hierarchy of
  households within groups.
- **Built-in drift event:** it includes a 2013 dynamic time-of-use tariff trial, a genuine
  distribution shift for the drift monitoring to detect.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| [NESO Historic Demand Data](https://www.neso.energy/data-portal/historic-demand-data) | Half-hourly national demand (ND, TSD), embedded wind/solar, interconnectors, 2001–present | CSV per year + CKAN API, no key | NESO Open Data Licence |
| [Low Carbon London smart meters](https://data.london.gov.uk/dataset/smartmeter-energy-use-data-in-london-households/) | 5,567 households, half-hourly kWh, Nov 2011–Feb 2014; tariff group (Std/ToU) and the 2013 ToU price schedule | London Datastore (~765 MB zip → 11 GB CSV, 167M rows) | CC BY |
| [Open-Meteo historical API](https://open-meteo.com/) | Temperature, solar radiation, wind for UK locations | Free, no key; rate-limited | CC BY 4.0 data; **free tier is non-commercial** (fine for a portfolio) |
| *Optional:* Elexon BMRS | Demand outturn, cross-check | API, no key | Check terms |

## Scope

**Must have**
- **Data:**
  - Ingestion with Parquet storage and data-quality checks (Pandera or Great Expectations).
  - Handle clock-change days, which have 46 or 50 settlement periods.
- **National model, a ladder of models:**
  - seasonal naive
  - LightGBM with calendar and weather features
  - quantile LightGBM with conformal calibration
- **Household model:**
  - PyMC hierarchical model: household → group → global.
  - Compare against per-household and pooled LightGBM on MAE (mean absolute error) and interval coverage, especially for households with little history.
- **Platform:**
  - A Prefect flow: ingest → validate → train → evaluate → register (MLflow) → promote only if it beats the current production model on a rolling backtest.
  - Evidently drift reports. On LCL, replay time through 2013 and show the ToU trial triggering drift alerts.
  - A FastAPI `/forecast` endpoint and a Streamlit dashboard (forecast fan chart, calibration plot, drift status).

**Stretch:** Terraform for an AWS Lambda service + EventBridge scheduled job; a hierarchical reconciliation check (households sum sensibly to group totals).

**Out of scope:** real-time intraday trading forecasts; generation forecasting.

## Design decisions to write up

- Choosing the backtest window and how a model gets promoted.
- Calibration vs sharpness, and why pinball loss alone isn't enough.
- When partial pooling helps (sparse groups) and when it doesn't.
- The cost of the Bayesian model: sampling time vs benefit, and the use of variational inference.

## Risks and gotchas

- The **LCL file is large** (11 GB CSV). Convert to partitioned Parquet once and sample households for development.
- **ACORN socio-demographic groups** may only be in the refactored 4TU copy of LCL (*unverified*). Fall back to tariff group + clustering on load shape as the hierarchy.
- **Embedded solar/wind in NESO data is modelled, not metered**, so note the implications for features.
- Use Open-Meteo's archive once and cache the results to stay within its rate limits.

## Done when

- [ ] Scheduled daily run on NESO data with MLflow history visible
- [ ] Calibration plots for both models in the README
- [ ] Drift report showing the 2013 ToU trial detected
- [ ] Hierarchical vs LightGBM comparison table, with an honest verdict
