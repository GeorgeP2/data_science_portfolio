# Fulfilment Optimisation

> **Category:** MLOps & Deployment · **Status:** 🚧 In progress

## Problem

> For a manual picker-to-parts warehouse, how much walking distance can batching and routing
> optimisation save compared with first-come-first-served greedy batching, and what does each
> extra millisecond of solve time buy?

An order-batching and pick-path optimisation API that beats a greedy baseline within a hard latency
budget, benchmarked against published academic instances so the claims can be checked.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="reports/figures/pareto_dark.png">
  <img alt="Walking distance saved against first-come-first-served batching, by solve time, for seed, savings, ALNS and CP-SAT under S-shape and largest-gap routing" src="reports/figures/pareto.png">
</picture>

Savings captures most of the gain in about 10 ms: 24% less walking than FCFS with S-shape
routing. ALNS adds 2 points by 100 ms and 4.7 by 10 s. CP-SAT stays just below ALNS at every
budget and only draws level at 10 s ([data](../../docs/projects/p1-fulfilment-optimisation/results/pareto.md)).

## Data

| Source | What | Licence | Use |
|--------|------|---------|-----|
| [KIT Manual Warehouse Order Picking benchmarks](https://doi.org/10.35097/mwsv59v8sk9sqaan) (Barlang, Lehmann, Furmans, 2026) | 2.0 GB JSON: layouts, orders per shift, lines per order, arrival randomness, due dates and storage policies; 132 designed parameter sets (32 one-factor-at-a-time + 100 Latin hypercube) × 100 replications | CC BY 4.0 | Calibrate the generator's parameter ranges; stress scenarios |
| [Henn & Wäscher (2012) batching instances](https://grafo.etsii.urjc.es/optsicom/obsp.html) | 96 instances: 10 aisles × 90 locations, depot bottom-left, 20–80 orders, capacity 45 or 75, due dates | Not stated: fetched by script, not redistributed | External benchmark |
| [Arbex Valle et al. Foodmart instances](https://homepages.dcc.ufmg.br/~arbex/orderpicking.html) | 8/16-aisle single- and dual-block layouts, 1,560 SKUs, 5–5,000 orders | Not stated: fetched by script, not redistributed | External benchmark + realistic SKU/order-size distributions |
| Own generator | Parameterised warehouse + order stream | MIT | Everything else |

Raw data lives in `data/raw/` and is never committed. Instances without a stated licence are
downloaded by script rather than redistributed; see [`data/README.md`](data/README.md).

## Approach

The warehouse is a single block of parallel aisles with the depot in front of aisle 0, using the
Henn & Wäscher (2012) geometry so distances are comparable with the published instances. Each order
is a set of pick locations, and a picker can carry a fixed number of items per tour.

**Batching solvers** group orders into tours. All share one interface (`solvers/base.py`): a
solver takes a deadline, publishes improvements to a thread-safe incumbent, and returns its best
solution.

| Solver | What it does | Reference |
|--------|--------------|-----------|
| FCFS (baseline) | Fills each tour in arrival order until the next order doesn't fit | – |
| Seed | Seeds each tour with the order visiting most aisles, then adds the orders that add the fewest new aisles | de Koster et al. (1999) |
| Savings | Merges the pair of tours with the largest distance saving, re-costing exactly after every merge (C&W(ii)) | de Koster et al. (1999) |
| ALNS | Adaptive large neighbourhood search from the savings start: 3 destroy and 2 repair operators, simulated annealing, adaptive weights, cached tour costs | Ropke & Pisinger (2006) |
| CP-SAT | Set partitioning over a pool of candidate tours, each costed exactly; exact on ≤ 12 orders, otherwise the pool comes from ALNS | OR-Tools |

**Routing** turns a tour's picks into a walk (`routing/`): S-shape, largest-gap, and optimal
routing by Ratliff & Rosenthal's (1983) dynamic programme over aisles, checked against brute force.
Batching solvers only ask the router for tour lengths, so routing policies are interchangeable.

**Benchmark harness** (`benchmark.py`) runs every solver × router × instance × time limit from
`config.yaml` in a process pool, checks every solution is feasible, and writes
`outputs/runs.parquet` and `outputs/metrics.json`.

**Service** (`api/`): `POST /batch` takes orders, a layout, picker capacity, a solver, a router and
`budget_ms`. The budget is a hard limit on server-side response time: FCFS is computed first, the
chosen solver runs in a worker thread, and at the deadline the service returns the solver's best
solution so far, or FCFS (`fallback_used: true`) if there is nothing better. Requests over the
order limit get 413; requests that can't be solved as given (an order over capacity, a pick
outside the layout) get 422 with a message.

## Results

_Interim: the Pareto chart over budgets is still to come._

Distance saved against FCFS with the same routing policy, at a 1 s budget:

| Solver | S-shape | Largest gap | Optimal routing | Solve time p50 / p95 |
|--------|--------:|------------:|----------------:|---------------------:|
| FCFS (mean tour distance, LU) | 6,035 | 5,762 | 5,080 | < 0.1 ms |
| Seed | 15.2% | 10.6% | 11.7% | 0.6 / 1.5 ms |
| Savings | 24.4% | 20.7% | 19.8% | 11–12 / 38–41 ms (95 / 295 ms with optimal) |
| ALNS | **27.6%** | **23.2%** | 21.7% | uses the budget |
| CP-SAT | 27.2% | 22.7% | **22.2%** | uses the budget |

Mean over 96 instances per routing policy, on a laptop CPU. ALNS and CP-SAT are never worse than
savings on any instance; seed is worse than FCFS on 2 per routing policy.

**Routing matters as much as batching.** On the same tours, S-shape walks 19.7% and largest gap
16.2% further than optimal routing (1,308 tours built by savings). Percentages above are against
FCFS *with the same routing*, so optimal routing looks smaller there only because FCFS benefits
too: in absolute terms, CP-SAT with optimal routing walks 3,939 LU on average, **34.7% less than
FCFS with S-shape**, against 27.8% for the best S-shape result. With optimal routing, CP-SAT
overtakes ALNS (better on 48 of 96 instances): the exact router is about 15× slower per call, so
ALNS gets fewer iterations, while CP-SAT proves its pool optimal in 65% of runs.

**Held-out generated scenarios** (run once on seeds never used in development, with settings frozen
in a commit beforehand; [full tables](../../docs/projects/p1-fulfilment-optimisation/results/held_out.md)).
KIT-style shifts are batched per 30-minute arrival window at 1 s per window. Saved against FCFS
with S-shape routing:

| Scenario | Seed | Savings | ALNS | CP-SAT |
|---|---:|---:|---:|---:|
| `baseline` (KIT standard case) | 26.5% | 39.6% | **42.8%** | 42.6% |
| `peak_day` (2,000 orders, waves) | 37.8% | 49.7% | 50.3% | **50.3%** |
| `high_affinity` | 31.6% | 46.1% | **48.2%** | 48.1% |
| `henn_waescher_like` | 16.5% | 26.3% | **28.7%** | 27.2% |

Small KIT-style orders batch many to a tour, so the savings are larger than on the benchmark.
The ranking holds on every scenario. One cell failed, and it's reported as it came out: **peak
day with optimal routing**. Windows of 90-300 orders were too large for the exact router at 1 s.
Savings ran out of time while costing all order pairs in 73 of 160 windows and returned
single-order tours, 4.8 times FCFS's distance (−304% on average). ALNS and CP-SAT, which start
from savings, got almost no search time (8% and 5%). The service isn't exposed to this, because its
runner returns FCFS whenever a solver's answer is worse. Making savings fall back to FCFS, and
capping the exact router's use on large windows, are follow-ups to test on development seeds.

**Against published results.** No per-instance distances are published for these instances, so
the check is relative: each solver's improvement over C&W(ii) savings, per class, against Henn &
Wäscher's best method (ABHC*, within 0.1–1.4% of optimal) on their instances from the same
generator. The tolerance, set before the per-class results were computed, is 1 percentage point
below theirs. ALNS is within it on **12 of 12** shared classes at 10 s and at 60 s, but on only 4
of 12 at 1 s: larger instances need more iterations
([full table](../../docs/projects/p1-fulfilment-optimisation/results/published_comparison.md)).
With S-shape routing, ALNS improves on savings by 1–3 points *more* than ABHC*, which says more
about the baseline or the instance sample than about ALNS beating a near-optimal method; the
relative measure can't separate small differences.

The published per-instance values are tardiness, not distance. Reproducing the published EDD
tardiness didn't work: our values are 0.3–0.6× theirs, although our single-order processing
times match the generator that produced the instances' due dates (R² 0.994). What was tried is
in [`references/README.md`](references/README.md).

**Service latency** (ALNS, requests of 10–300 orders, server-side time from the `Server-Timing`
header): with a 50 ms budget, p99 is 22.7 ms on the laptop, since the solver stops 30 ms early to
leave time for the response. On one emulated x86 CPU, closer to a small cloud instance, the
slowest of 300 requests took 50.6 ms. Live numbers come with the deploy.

## Key takeaways

Interim, from the 1 s results above:

- **Savings captures most of the gain.** It saves 21–24% in tens of milliseconds; ALNS adds
  another 2–4 points with a full second.
- **ALNS needs more than 1 s on 60+ orders to match published quality.** At 10 s it is within
  1 point of the best published method on every shared class. The largest-gap router is 4.5×
  slower per call than S-shape, so it gets fewer iterations per second.
- **Optimal routing is worth more than a better batching heuristic.** The heuristics walk 16–20%
  further than optimal on the same tours, more than ALNS gains over savings.
- **CP-SAT doesn't beat ALNS at any budget up to 10 s** with the fast heuristic routers. Half the budget goes on building its
  pool, which costs more than recombining tours gains back; it draws level only at 10 s. It proves optimality over its pool on 71% of 20-order
  instances, but almost never at 40 orders or more.
- **A hard latency budget takes engineering beyond the solver.** Keeping p99 under budget needed
  the clock to start when the request arrives, the response built without nested pydantic models,
  and garbage collection moved between requests.
- **Limitation:** everything assumes a single-block rectangular layout, the benchmarks' geometry.
  Real sites are often irregular; graph-defined layouts are planned as phase 3.

## Design decisions and trade-offs

### 1. Batching model: CP-SAT set partitioning, not a MIP

**Chosen:** the model picks tours from a pool of candidates, each costed exactly by the router,
so that every order is covered once (`solvers/cp_sat.py`). Tour length isn't linear in which orders
share a tour, so a compact model would have to approximate distance; set partitioning keeps
distance exact and puts the approximation in the pool instead. CP-SAT solves it because the model
is pure 0/1 with exactly-one constraints (its home ground), it accepts a full solution hint, it
reports every improving solution through a callback (needed for the latency budget), and it's
already in OR-Tools.

**Alternative: a MIP solver** (e.g. HiGHS or SCIP) on the same model. Set-partitioning LP
relaxations are tight, so a MIP would likely prove optimality over large pools faster and report
a gap. It wasn't benchmarked here, so that stays a hypothesis.

**What was measured is CP-SAT against ALNS.** With fast heuristic routers, ALNS is on the Pareto
frontier at every budget from 0.1 to 10 s, and CP-SAT only draws level at 10 s
([Pareto data](../../docs/projects/p1-fulfilment-optimisation/results/pareto.md)). Building the pool costs half the budget, which outweighs what
recombining tours wins back; CP-SAT proves its pool optimal in 71% of 20-order runs but almost never
at 40+ orders at 1 s. With the exact router, which is about 15× slower per call, ALNS gets far
fewer iterations and CP-SAT wins (22.2% vs 21.7% saved, better on 48 of 96 instances; README
results table above). **Which solver is better depends on how expensive routing is.**

### 2. Anytime solving under a hard latency budget

**Chosen:** every solver checks a shared deadline itself and publishes each improvement to a
thread-safe incumbent (`solvers/base.py`). The service computes FCFS first, runs the chosen solver
in a worker thread until `budget_ms` minus a 30 ms margin, and returns the solver's result, its
best-so-far, or FCFS, whichever is best (`api/runner.py`). A late worker is abandoned, not killed.

**Alternative: a process per request, killed at the deadline.** Rejected: starting a process costs
more than most budgets, and the best-so-far would have to cross a process boundary.

**Keeping the budget hard took more than the solver.** On a slow CPU the first version answered in
106-125 ms at a 50 ms budget (CI, reproduced in a 1-CPU emulated container). Three fixes, each
measured: start the clock when the request arrives (parsing 300 orders took ~24 ms), build the
response as plain JSON instead of ~1,000 nested pydantic models (~45 ms), and collect garbage
between requests rather than during them (27-37 ms pauses). Now p99 is 22.7 ms at a 50 ms budget on
a laptop, and the slowest of 300 requests on the emulated CPU took 50.6 ms
(`tests/test_api_budget.py`, which asserts p99 ≤ budget + margin). The FCFS guard also earned its
place: in the held-out run, savings returned tours 4.8× FCFS's length when it ran out of time
([held-out notes](../../docs/projects/p1-fulfilment-optimisation/results/held_out.md#notes-added-after-the-run)); the service would have returned FCFS.

### 3. Generator validity

**Chosen:** a generator whose ranges come from the KIT suite (13,200 shifts;
[profile](../../docs/projects/p1-fulfilment-optimisation/results/kit_profile.md)), with order size as a preset: KIT orders are 1-3 lines, the Henn &
Wäscher benchmark's 4-24. It was checked against both with thresholds fixed beforehand
([validity](../../docs/projects/p1-fulfilment-optimisation/results/generator_validity.md)): KIT's standard case matches (total variation distance
0.003 on lines and aisles per order), mean aisles per order across all 132 KIT settings is within
0.022, and solvers rank identically on generated and published Henn & Wäscher instances (Spearman
1.00, each within 0.3-1.6 points).

**Alternative: benchmark only on the published instances.** Rejected: 96 fixed instances invite
over-tuning and can't express peak days or affinity, and KIT alone has none of the large orders
the batching literature uses.

**Mismatches, stated:** the preset built from Henn & Wäscher's paper failed on aisles visited
(0.207) because their instance files differ from the paper (orders 4-24 not 5-25; class B in two
aisles not three); a preset corrected to the files passes (0.036), and both are reported. KIT's
Latin hypercube settings label a wave stochasticity that has no effect on arrivals (r = 0.00), so
waves are calibrated on its one-factor settings. Generated orders visit 0.027 fewer aisles than
KIT's under A-closest-to-depot storage.

### 4. API contract

**Chosen:** `POST /batch` either returns a feasible answer within `budget_ms` or fails with a
reason (`api/app.py`, `tests/test_api.py`):

- **413** above 500 orders (`api.max_orders`): the request is too big to answer within any budget
  the service allows.
- **422** with a message when the request can't be solved as given: an order larger than the
  picker's capacity, a pick outside the layout, an unknown layout id, a budget over 10 s, or an
  invalid field (duplicate order ids, unknown solver).
- A slow or failing solver is never an error: the response carries `fallback_used` and `status`,
  and `solver` names whose tours were returned.

**Alternatives rejected:** silently dropping orders that don't fit (hides a data problem the
caller must fix), or letting requests wait past their budget when all workers are busy (they
fall back to FCFS at the deadline instead).

### Limitations

- **Layout:** everything assumes a single-block rectangular warehouse, the benchmarks' geometry.
  Real sites are often irregular; graph-defined layouts are planned as phase 3.
- **Published comparison is relative:** no per-instance distances exist for the benchmark, and the
  published tardiness values didn't reproduce ([notes](references/README.md)).
- **KIT-style picker capacity (20 items) is assumed:** KIT has none.
- **Exact routing on large windows:** too slow at 1 s per 30-minute window on peak days (held-out
  run); savings should fall back to FCFS and search should use a fast router there.
- **Deploy pending:** the live latency figure needs the Lambda deployment.

## Reproduce

```bash
# from the repo root, with the venv active (`make setup-all`, or at least the app and opt extras)
cd projects/01-fulfilment-optimisation
PYTHONPATH=src python -m fulfilment_optimisation.download henn_waescher  # instances → data/raw/
PYTHONPATH=src python -m fulfilment_optimisation.benchmark               # grid from config.yaml → outputs/
pytest
```

The Pareto chart needs a sweep over budgets (about 45 minutes). It runs in three parts so that
single-threaded ALNS can use one worker per performance core while CP-SAT, which runs 4 threads
per solve, gets fewer workers:

```bash
B="PYTHONPATH=src python -m fulfilment_optimisation.benchmark"
eval $B --solvers fcfs seed savings --time-limits 1 --workers 6 --output sweep_constructive.parquet
eval $B --solvers alns --time-limits 0.1 0.25 0.5 1 2 5 10 \
    --param alns.max_iterations=100000000 --workers 6 --output sweep_alns.parquet
eval $B --solvers cp_sat --time-limits 0.1 0.25 0.5 1 2 5 10 \
    --param cp_sat.pool_iterations=100000000 --workers 2 --output sweep_cp_sat.parquet
PYTHONPATH=src python -m fulfilment_optimisation.report  # → reports/figures/pareto*.png
```

The benchmark grid (solvers, routers, time limits, seeds) and every solver parameter are in
`config.yaml`. FCFS, seed and savings are deterministic. ALNS and CP-SAT are deterministic for a
fixed seed and iteration cap, but under a time limit the number of iterations depends on machine
speed, so their numbers vary slightly between runs.

## Run locally

The service runs in a container. Build from the repo root, since the image includes the shared
`src/portfolio` package:

```bash
docker build -f projects/01-fulfilment-optimisation/Dockerfile -t fulfilment-optimisation .
docker run --rm -p 8080:8080 fulfilment-optimisation
```

In another terminal:

```bash
curl -s localhost:8080/batch -H 'Content-Type: application/json' \
  -d @projects/01-fulfilment-optimisation/examples/batch_request.json
```

The response lists each batch's orders and its picker route, with the total distance. Interactive
API docs are at <http://localhost:8080/docs>.

The image is 126 MB compressed (577 MB unpacked, most of it OR-Tools). It contains no benchmark
data: its ignore file lets in only the code and `config.yaml`.

## Skills demonstrated

- Optimisation modelling: set partitioning in CP-SAT, and when an exact model loses to a heuristic
- Metaheuristics: ALNS with adaptive operator weights and simulated annealing, built from scratch
- Classic OR heuristics: seed batching, Clarke & Wright savings, S-shape and largest-gap routing
- Anytime algorithms behind a hard latency budget, with a thread-safe incumbent and FCFS fallback
- Performance work: cost caching, incremental insertion costs, response building and GC tuning
- Benchmarking: a reproducible grid with feasibility checks on every result
- Service engineering: FastAPI contract with clear 413/422 errors, multi-stage Docker image
