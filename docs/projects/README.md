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

Two themes tie the projects together: **UK energy** (Projects 4 and 5 share households, prices
and weather) and **operations** (Projects 1 and 3). There is also a **decisions under uncertainty**
thread (Projects 5 and 8).

## Portfolio

| # | Project | Headline data | Core skills | Suggested order |
|---|---------|---------------|-------------|-----------------|
| 1 | [Fulfilment Optimisation Service](p1-fulfilment-optimisation/brief.md) | Own generator, calibrated on KIT and academic order-picking benchmarks | OR, CP-SAT, heuristics, simulation, APIs | 1st |
| 3 | [Rail Delay Copilot](p3-rail-delay-copilot/brief.md) | Network Rail delay attribution + the DAPR rulebook | RAG, text-to-SQL, agents, MCP, evals, LoRA | 2nd |
| 2 | [Experimentation & Uplift](p2-experimentation-uplift/brief.md) | Yale ISPS field experiment (344k people) + ASOS experiments | CUPED, cluster-robust inference, sequential tests, uplift | 3rd |
| 4 | [Energy Demand Forecasting Platform](p4-energy-forecasting-platform/brief.md) | Low Carbon London smart meters + NESO national demand | Forecasting, probabilistic + Bayesian models, MLOps | 4th |
| 7 | [Real-Time Card Fraud Scoring](p7-realtime-fraud-scoring/brief.md) | IBM TabFormer transactions + Feedzai BAF | Streaming, entity state, cost-sensitive decisions, fairness | 5th |
| 5 | [Time-of-Use Pricing Engine](p5-tou-pricing-engine/brief.md) | Own simulator, calibrated on Octopus Agile prices and the LCL tariff trial | Constrained optimisation, bandits, off-policy evaluation | 6th (pick 5 **or** 6) |
| 6 | [Two-Stage Music Recommender](p6-two-stage-recommender/brief.md) | Yandex Yambda (organic vs recommended listens) | Retrieval + ranking, offline eval, serving | 6th (optional) |
| 8 | [Powerlifting Attempt Selection Optimiser](p8-attempt-selection-optimiser/brief.md) | OpenPowerlifting (public domain, every attempt at every meet) | Bayesian latent-variable models, calibration, dynamic programming | Alongside 5/6 |

Numbers 1–7 match the roadmap; 8 was added afterwards. The order column is the build order.

## Every project ships with

- A README that **leads with the result**: one chart plus three bullets, then an architecture diagram.
- A **"Design decisions & trade-offs"** section.
- Tests, a CI badge, a Dockerfile and a one-command local run.
- A live demo where it's cheap to host (Cloud Run, Streamlit, or a Hugging Face Space).
- A `data/README.md` (in the code folder) with a download script, licence and attribution. Raw data is never committed.

## Before starting any project

- [ ] Re-check the dataset's URL and licence. Both change, and several are flagged *unverified* in the briefs.
- [ ] Write the download script first and pin the file checksums.
- [ ] Set a time box. At ~6–8 h a week, a missed milestone means cutting scope, not extending the deadline.
