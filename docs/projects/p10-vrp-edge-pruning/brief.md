# Project 10: Learned Edge-Pruning for VRP Solvers

**One line:** a graph neural network that scores which edges belong in good vehicle-routing
solutions, used to replace the distance-based neighbour lists inside a state-of-the-art HGS solver.

**Time box:** ~12 weeks part-time, plus an optional ~4-week serving phase. Flagship of the ML × OR track; build straight after Project 9.

## Headline question

> Does a learned edge-pruning model help a state-of-the-art VRP solver reach a given solution
> quality faster on large instances, with model inference counted in the wall clock?

## Why it matters

Pure neural solvers still trail strong metaheuristics like HGS on large instances. A hybrid that
measurably helps HGS is a result OR and ML researchers both respect.

## Data

| Source | What | Access | Licence | Use |
|--------|------|--------|---------|-----|
| [Uchoa et al. X set (CVRPLIB)](http://vrp.galgos.inf.puc-rio.br/index.php/en/) | CVRP instances, 100–1000 customers, with best-known solutions | Open download | *Unverified*: download via script | Held-out evaluation |
| Gehring & Homberger | VRPTW instances, 200–1000 customers | Open download (URL *unverified*) | *Unverified* | Stretch evaluation |
| **Own generator** | Synthetic instances matching X-set distributions, labelled with edges from long-run HGS solutions | In repo | MIT | Training data |

## Scope

**Must have**
- **Baseline:** PyVRP (open-source HGS). Its local search accepts custom neighbour lists, which is the integration point.
- **Edge model:** a GNN on a sparse k-nearest-neighbour graph that scores each edge's likelihood of being in a good solution.
  - Features: distance, neighbour rank, demand/capacity ratio.
- **Training labels:** edges in long-run HGS solutions on synthetic instances matching X-set distributions.
- **Solver integration:** top-k scored edges replace the distance-based neighbourhood in local search. Variants mix learned and distance neighbours.
- **Ablations:** k, mixing ratio, and a random-pruning control.
- **Evaluation:** time-to-gap curves, primal integral, paired tests and size generalisation.

**Stretch**
- VRPTW on Gehring & Homberger, adding time-window overlap as an edge feature.

**Out of scope:** new metaheuristics, pure end-to-end neural construction, real-world routing data.

## Milestones

| Weeks | Milestone | Exit criterion |
|-------|-----------|----------------|
| 1–2 | Benchmark harness | PyVRP's published gaps reproduced within tolerance |
| 3–4 | Instance generator + labels | 50k+ labelled instances across X-set distributions |
| 5–7 | Edge model | Edge recall ≥ 95% at k = 10 on held-out data |
| 8–9 | Solver integration + ablations | End-to-end runs across k, mixing ratio, random-pruning control |
| 10–11 | Evaluation | Time-to-gap curves, primal integral, paired tests, size generalisation |
| 12 | Release | Repo, write-up, racing demo |

## Deliverables and headline chart

- **Time-to-gap curves** for learned pruning vs default PyVRP.
- A paper-style write-up.
- A demo showing both solvers racing on one instance.

## Design decisions to write up

- Learned vs distance-based neighbourhoods, and how much mixing is needed.
- Counting inference in the wall clock, and keeping the model small enough for it to pay off.

## Risks and gotchas

- **Inference cost wipes out the gain.** Measure end to end from week 1 and keep the model small.
- **Overfitting to the generator.** Hold out real benchmark families entirely.
- **Small gains on CVRP.** Pivot the headline to VRPTW, where pruning has more room.

## Done when

- [ ] Statistically significant primal-integral improvement over default PyVRP at equal wall clock, inference included, on held-out benchmark instances. A rigorous negative result still ships.
- [ ] One-command reproduction
- [ ] README leads with the time-to-gap curves

**Stack:** PyTorch Geometric, PyVRP, Hydra, Weights & Biases.

## Phase 2: serving case study (~4 weeks, optional)

Inference cost is this project's main risk, so it's the natural model for a serving case study.
Take the edge model from a plain FastAPI + PyTorch baseline through a measured optimisation
ladder, proving the ability to ship, not just train, with real numbers.

**Headline question:** how far can systematic optimisation cut serving cost per 1k requests while
holding a stated p99 latency target and accuracy floor?

**Must have**
- **Targets:** p99 latency, throughput and accuracy floor, fixed before optimising.
- **Baseline:** plain FastAPI + PyTorch eager, load-tested with a realistic request mix.
- **Optimisation ladder, measured step by step:** ONNX or TorchScript export, dynamic batching, quantisation, CPU vs GPU choice, caching.
- **Observability:** latency histograms, an input drift monitor, alerting on accuracy proxies.
- **Cost model:** cost per step using public cloud pricing.

**Out of scope:** multi-region deployment, Kubernetes operators, autoscaling policy research.

| Weeks | Milestone | Exit criterion |
|-------|-----------|----------------|
| 1 | Baseline + load test | Reproducible latency and cost numbers |
| 2–3 | Optimisation ladder | Each step measured on latency, cost, accuracy |
| 4 | Monitoring + write-up | Dashboard, drift demo, release |

**Risks**
- **Benchmarks look staged.** Publish the load-test scripts and request traces.
- **Cloud prices change.** Date the cost model and keep the unit maths explicit.

**Done when**
- [ ] Waterfall of cost per 1k requests after each step, with latency and accuracy held within target throughout
- [ ] Load-test scripts and request traces published
- [ ] Monitoring dashboard and drift demo

**Stack:** FastAPI, ONNX Runtime, Triton or Ray Serve, Locust or k6, Prometheus and Grafana.
