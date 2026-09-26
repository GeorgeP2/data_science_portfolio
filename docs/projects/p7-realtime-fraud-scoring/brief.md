# Project 7: Real-Time Card Fraud Scoring

**One line:** a streaming fraud scorer. It replays 24M card transactions through Redpanda, keeps
per-card state for velocity features, scores each transaction within a latency SLO and picks
decision thresholds by expected cost. A companion analysis audits model fairness.

**Time box:** weeks 23–26 (~30 h).

## Headline questions

> 1. At a p99 latency budget of ≤50 ms per transaction, how much expected fraud loss does the
>    model prevent, net of the cost of false declines?
> 2. How much do stateful, real-time features (per-card velocity, merchant novelty) add over
>    static features, and what do they cost in latency and infrastructure?
> 3. *(Companion)* Does a threshold chosen to minimise cost produce very different false-positive rates across age groups?

## Why this data is different

IEEE-CIS is the default and it's poorly suited to streaming: it's anonymised, has no stable entity
key and needs a time-split workaround. **IBM TabFormer** has real user and card IDs and timestamps,
so the streaming and state-management work is genuine. **Feedzai BAF** is a
NeurIPS benchmark designed for fairness evaluation.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| [IBM TabFormer card transactions](https://github.com/IBM/TabFormer) | ~24M synthetic transactions: User, Card, timestamp, Amount, Use Chip, Merchant Name/City/State, MCC, Errors, Is Fraud | Box link / Git LFS from the repo | Code Apache 2.0; **data licence unverified**, so download via script and never redistribute |
| [Feedzai Bank Account Fraud (BAF)](https://www.kaggle.com/datasets/sgpjesus/bank-account-fraud-dataset-neurips-2022) | 6 variants × 1M account applications, 32 features, `month` 0–7, `fraud_bool`; age/income/employment attributes | Kaggle login | Apache 2.0 + "contact Feedzai for commercial use" (portfolio use is fine) |

## Scope

**Must have**
- **Offline model:**
  - Time-aware split (train on early months, validate, test on the latest).
  - LightGBM with static features, then with stateful features: velocity counts/sums over 1h/24h/7d, time since last transaction, new merchant or MCC for this card, amount z-score against the card's history.
- **Evaluation:** precision-recall AUC, recall at a fixed false-positive rate, and **cost curves**. A missed fraud costs its amount; a false decline costs a margin plus a churn penalty.
- **Threshold choice:** threshold chosen by minimising expected cost, with a sensitivity analysis on the cost assumptions.
- **Streaming:**
  - A producer replays TabFormer in event-time order into Redpanda, keyed by card.
  - The scorer consumes, updates per-card state (in-memory → Redis), scores and emits a decision.
- **Parity:** a test proves the streaming features equal the offline features (the classic training/serving skew bug).
- **Load test:** p50/p99 latency under replay at N× real time, reported against the SLO.
- **Docker Compose:** `make up` starts Redpanda + scorer + a small Grafana or Streamlit monitor.

**Companion (BAF)**
- Train on months 0–5, test on 6–7.
- Compare false-positive rate and recall by age group at the cost-optimal threshold, and try group-aware thresholds.
- Discuss the trade-offs honestly; don't moralise.

**Stretch:** delayed-label simulation (fraud labels arrive days later) and its effect on monitoring; a graph feature (shared merchants between flagged cards).

**Out of scope:** the Elliptic2 graph / anti-money-laundering (AML) problem; deep sequence models.

## Design decisions to write up

- Where state lives (in-process vs Redis vs a stream processor) and failure recovery.
- Event time vs processing time; handling out-of-order events.
- Why AUC isn't the business metric.
- Latency budget breakdown: deserialisation, feature lookup, inference, publish.

## Risks and gotchas

- TabFormer is **synthetic**, so be upfront about it; the engineering is the point.
- **Extreme class imbalance:** use proper stratified evaluation and don't report accuracy.
- **Timestamps are minute-level**, so ties need a deterministic ordering.
- The BAF commercial-use clause means it stays in a portfolio / non-commercial context.

## Done when

- [ ] `make up && make replay` shows live scoring with a latency panel
- [ ] Feature-parity test in CI
- [ ] Cost curve + chosen threshold in the README
- [ ] Fairness companion section with the group metrics table
