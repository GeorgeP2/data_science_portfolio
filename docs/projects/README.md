# Projects

One folder per planned project:

```
pN-project-name/
├── brief.md    # question, data, scope, definition of done: written before any code
└── results/    # findings, charts and write-ups as the project progresses
```

Code lives separately in `projects/NN-name/` at the repo root. When a project starts, run
`make new-project` and copy the brief's headline question and data table into the code folder's README.

## Data principle: no Kaggle staples

Every project uses data that most portfolios don't: UK open data, recent research releases, or a
generator I wrote myself. There are two reasons:

1. A reviewer who has seen fifty Titanic / Criteo / M5 / IEEE-CIS notebooks learns nothing from a fifty-first.
2. Messy, under-documented public data forces the real work: finding the data, cleaning it,
   deduplicating it and reasoning about how it was generated. That work is the job.

Two themes tie the projects together: **UK energy** (Projects 4, 6 and 11 share households, prices
and weather) and **operations** (Projects 1 and 2). There is also a **decisions under uncertainty**
thread (Projects 6 and 8). Projects 9–12 add an **ML × OR** track (see below).

## Portfolio

| # | Project | Headline data | Core skills | Notes |
|---|---------|---------------|-------------|-------|
| 1 | [Fulfilment Optimisation Service](p1-fulfilment-optimisation/brief.md) | Own generator, calibrated on KIT and academic order-picking benchmarks | OR, CP-SAT, heuristics, simulation, APIs | |
| 2 | [Rail Delay Copilot](p2-rail-delay-copilot/brief.md) | Network Rail delay attribution + the DAPR rulebook | RAG, text-to-SQL, agents, MCP, evals, LoRA | |
| 3 | [Experimentation & Uplift](p3-experimentation-uplift/brief.md) | Yale ISPS field experiment (344k people) + ASOS experiments | CUPED, cluster-robust inference, sequential tests, uplift | |
| 4 | [Energy Demand Forecasting Platform](p4-energy-forecasting-platform/brief.md) | Low Carbon London smart meters + NESO national demand | Forecasting, probabilistic + Bayesian models, MLOps | |
| 5 | [Real-Time Card Fraud Scoring](p5-realtime-fraud-scoring/brief.md) | IBM TabFormer transactions + Feedzai BAF | Streaming, entity state, cost-sensitive decisions, fairness | |
| 6 | [Time-of-Use Pricing Engine](p6-tou-pricing-engine/brief.md) | Own simulator, calibrated on Octopus Agile prices and the LCL tariff trial | Constrained optimisation, bandits, off-policy evaluation | Pick 6 **or** 7 |
| 7 | [Two-Stage Music Recommender](p7-two-stage-recommender/brief.md) | Yandex Yambda (organic vs recommended listens) | Retrieval + ranking, offline eval, serving | Optional |
| 8 | [Powerlifting Attempt Selection Optimiser](p8-attempt-selection-optimiser/brief.md) | OpenPowerlifting (public domain, every attempt at every meet) | Bayesian latent-variable models, calibration, dynamic programming | Alongside 6/7 |

Projects are numbered in build order.

## ML × OR track

A second set of briefs makes one claim: machine learning and operations research work together on
real logistics problems. Three flagship projects prove that claim; one range project shows depth
outside it. Some related ideas became extensions of existing projects instead: the warehouse
simulator is phase 2 of Project 1, the serving case study is phase 2 of Project 10, and the
late-deliveries causal study is a stretch goal in Project 3.

| # | Project | Role | Effort (part-time) | Headline artefact |
|---|---------|------|--------------------|-------------------|
| 9 | [LLM Optimisation Formulation](p9-llm-formulation/brief.md) | Flagship | 14 weeks (agent 8 + benchmark 6) | Verified-solution rate + public benchmark |
| 10 | [Learned Edge-Pruning for VRP](p10-vrp-edge-pruning/brief.md) | Flagship | 12 weeks (+4 serving phase) | Time-to-gap curves vs HGS |
| 11 | [Forecast-to-Procurement Pipeline](p11-forecast-to-procurement/brief.md) | Flagship | 8 weeks | Cost vs shortfall-rate frontier |
| 12 | [Small Transformer from Scratch](p12-transformer-from-scratch/brief.md) | Range | 6 weeks | Scaling-law plots |

## Build order

Projects are numbered in build order: 1 → 8, picking 6 **or** 7, with 8 alongside them. Then the
ML × OR track: 9 → 10 → 11. Project 9 builds on 2's agent and eval work, and together 9 and 10 tell
one story: learned guidance inside exact optimisation. Project 11 reuses Project 4's data. P1
phase 2, P10 phase 2 and Project 12 are optional.

## Ground rules

- Public or synthetic data only. No employer data, code, internal methods or benchmarks. Build on
  personal time and hardware.
- One falsifiable claim per project, stated before the work starts.
- Strong baselines, multiple seeds, ablations, and a section on what didn't work.
- One-command reproduction in CI. Every figure in a write-up regenerates from the repo.

## Every project ships with

- A README that **leads with the result**: one chart plus three bullets, then an architecture diagram.
- A **"Design decisions & trade-offs"** section.
- A write-up, plus a demo or plot someone can grasp in 30 seconds.
- Tests, a CI badge, a Dockerfile and a one-command local run.
- A live demo where it's cheap to host (Cloud Run, Streamlit, or a Hugging Face Space).
- A `data/README.md` (in the code folder) with a download script, licence and attribution. Raw data is never committed.

## Before starting any project

- [ ] Re-check the dataset's URL and licence. Both change, and several are flagged *unverified* in the briefs.
- [ ] Write the download script first and pin the file checksums.
- [ ] Set a time box. At ~6–8 h a week, a missed milestone means cutting scope, not extending the deadline.
