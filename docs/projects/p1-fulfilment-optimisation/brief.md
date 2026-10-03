# Project 1: Fulfilment Optimisation Service

**One line:** an order-batching and pick-path optimisation API that beats a greedy baseline within
a hard latency budget. It is benchmarked against published academic instances, so the claims can
be checked.

**Time box:** weeks 1–6 (~40 h, including repo hygiene). Plays to existing strengths, so it should ship first.

## Headline question

> For a manual picker-to-parts warehouse, how much walking distance can batching and routing
> optimisation save compared with first-come-first-served greedy batching, and what does each
> extra millisecond of solve time buy?

## Why this data is different

Most optimisation portfolios solve toy TSPs. This one:
1. **Reproduces published benchmarks** (Henn & Wäscher; Foodmart-based instances). Matching or
   beating known results is instant credibility.
2. **Calibrates its own generator** on the 2026 KIT benchmark suite. It can then produce unlimited
   realistic scenarios, e.g. peak days, SKU affinity and tight due dates, which fixed benchmarks can't.

## Data

| Source | What | Access | Licence | Use |
|--------|------|--------|---------|-----|
| [KIT Manual Warehouse Order Picking benchmarks](https://radar.kit.edu/radar/en/dataset/mwsv59v8sk9sqaan) (Barlang, Lehmann, Furmans, 2026) | 2 GB JSON: layouts, orders per shift, lines per order, arrival randomness, due dates and storage policies across 132 designed parameter sets × 100 replications | Open download | CC BY 4.0 | Calibrate the generator's parameter ranges; stress scenarios |
| [Henn & Wäscher (2012) batching instances](https://grafo.etsii.urjc.es/optsicom/obsp.html) | 96 instances: 10 aisles × 90 locations, 20–80 orders, picker capacity 45 or 75 items, due dates | Open download (`obsp_instances.zip`) | Not stated: don't redistribute; download via script | External benchmark |
| [Arbex Valle et al. Foodmart instances](https://homepages.dcc.ufmg.br/~arbex/orderpicking.html) | 8/16-aisle layouts, 1,560 SKUs, 5–5,000 orders, plus a layout generator | Open download | Not stated: don't redistribute | External benchmark + realistic SKU/order-size distributions |
| **Own generator** | Parameterised warehouse + order stream | In repo | MIT | Everything else |

## Scope

**Must have**
- A generator (`layout`, `sku_affinity`, `order_arrivals`) with parameter ranges fitted to the KIT suite.
- A solver interface with 4 implementations: greedy FCFS (first-come-first-served) baseline, seed-and-savings heuristic, OR-Tools CP-SAT, and my own local search (e.g. ALNS). Routing covers S-shape, largest-gap and optimal routing per batch.
- A benchmark harness that runs every solver × instance with a time limit and reports gap to the best known solution, distance saved vs baseline and p50/p95 solve time.
- A FastAPI service: `POST /batch` takes orders and returns batches and routes. It has a **latency budget parameter** and falls back to the best solution found so far (or to greedy) when the budget runs out.
- A Dockerfile, deployment to AWS Lambda (container image behind a function URL), and a load test
  showing p95 latency under budget.

**Stretch**
- A discrete-event simulation (SimPy) of a full shift with dynamic arrivals, comparing batching every N minutes with batching every M orders.
- A Pareto chart of distance saved against solve-time budget.

**Out of scope:** automated/AS-RS warehouses, multi-picker congestion. Slotting is left to phase 2.

## Deliverables and headline chart

- The **distance-saved vs solve-time Pareto curve per solver**, on the published instances.
- A results table showing gap to the published best-known values.

## Design decisions to write up

- Why CP-SAT and not a MIP (mixed-integer programming) solver, and where each wins.
- Anytime algorithms and returning a solution under a deadline.
- Generator validity: how I showed the synthetic instances resemble the benchmarks (e.g. matching distributions of order size and aisles visited).
- API contract: what happens on infeasible or oversized requests.

## Risks and gotchas

- Benchmark instance licences are unstated, so fetch them with a script rather than vendoring them.
- It's easy to over-tune on 96 instances. Keep a held-out set of generated instances for the final numbers.
- **Confidentiality:** use only public literature and my own code. Nothing from employer systems.

## Done when

- [ ] `docker run` + one `curl` reproduces a batching result
- [ ] Benchmark table reproduces the published instance results within a stated tolerance
- [ ] Live AWS Lambda endpoint with a documented p95 latency
- [ ] README leads with the Pareto chart

## Phase 2: open warehouse simulator (~10 weeks, optional)

Turn the phase 1 generator, layouts and routing into an open, fast, Gymnasium-compatible simulator
that lets RL and OR methods be compared fairly on slotting and picking, and shows where each wins.
Warehouse research lacks a shared benchmark, so published results are hard to compare, and a tool
other people adopt builds reputation faster than any single result.

**Headline question:** on slotting and picking, where do learned (RL) methods beat classic OR
heuristics, and where don't they?

**Must have**
- **Engine:** the phase 1 core with a Rust (PyO3) or Numba hot path. Target 10k+ orders simulated per second on a laptop.
- **Layouts:** configurable aisles, cross-aisles, depot position and rack heights.
- **Tasks:** SKU slotting (static and periodic re-slot), on top of phase 1's batching and routing.
- **Demand:** synthetic order streams with tunable SKU popularity skew and affinity between SKUs.
- **APIs:** Gymnasium for RL, plus a plain function API for OR methods.
- **Baselines:** ABC slotting and correlation-based slotting, plus phase 1's routing heuristics.
- **Learned methods:** PPO for dynamic re-slotting, and a learned batching policy.
- **Benchmark:** a scenario suite with fixed seeds and a public leaderboard.

**Out of scope:** robotics physics, labour scheduling, real facility data.

| Weeks | Milestone | Exit criterion |
|-------|-----------|----------------|
| 1–3 | Engine speed-up + layouts | Travel distances match phase 1; speed target met |
| 4–5 | Slotting baselines | Classic heuristics reproduce known relative orderings |
| 6–8 | RL agents | Learned policies trained on 3+ scenarios |
| 9–10 | Docs, leaderboard, release | pip-installable package, docs site, results table |

**Risks**
- **Scope creep into a full digital twin.** Freeze the feature list at week 3.
- **RL underperforms simple heuristics.** That is still a finding; publish the regime map honestly.

**Done when**
- [ ] A new user installs the package and runs a baseline in under five minutes
- [ ] Regime map of where learned methods beat heuristics, in the README
- [ ] Docs site and leaderboard live

**Stack:** Numba or Rust (PyO3), Gymnasium, Stable-Baselines3, OR-Tools.
