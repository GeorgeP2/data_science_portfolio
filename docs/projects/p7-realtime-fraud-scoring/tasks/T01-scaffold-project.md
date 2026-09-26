# T01: Scaffold the project

**Phase:** 0 Setup · **Estimate:** 1 h · **Depends on:** none

## Ask

Create the project folder with `make new-project` and set up its config and dependencies.

## Why

Every later task needs a package to import from, a `config.yaml` for tunables and a passing `make check`.
Using the generator keeps numbering, package naming and the README table consistent.

## How

- `make new-project name="Real-Time Card Fraud Scoring" category=mlops`. Package:
  `real_time_card_fraud_scoring`.
- Dependencies: the `ml` extra (LightGBM), a Kafka client that works with Redpanda
  (e.g. `confluent-kafka`), `redis`, and the `app` extra if the monitor is Streamlit.
- Copy the headline questions and the data table from `brief.md` into the project README.

## Plan

- [ ] Re-check both dataset URLs and licences (TabFormer's data licence is flagged *unverified*)
- [ ] Run `make new-project`
- [ ] Add dependencies and install them
- [ ] Seed `config.yaml` with `seed`, data paths, and empty `features`, `model`, `costs`, `stream` sections
- [ ] Paste headline questions and data table into the README
- [ ] `make check`

## Acceptance criteria

- [ ] The project folder exists and the root README table has its row
- [ ] `PYTHONPATH=src python -c "import real_time_card_fraud_scoring"` works from the project folder
- [ ] `make check` passes
- [ ] README states the headline questions and data sources with licences
