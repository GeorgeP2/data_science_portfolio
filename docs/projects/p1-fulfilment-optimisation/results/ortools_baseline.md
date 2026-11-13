# OR-Tools routing baseline

Google OR-Tools' vehicle routing solver, run as one more solver through the same benchmark harness
and time budgets as the others (`solvers/ortools_routing.py`, registered as `ortools`). Each
vehicle is one picker tour with capacity in items, so the orders on a vehicle are a batch. Its
batches are re-scored with our routers, so every number here uses the same cost function as the
other solvers. The run's numbers come from `outputs/sweep_ortools.parquet` and
`outputs/ortools_pick_nodes.parquet` (commands below), compared with the existing
`sweep_constructive.parquet`, `sweep_alns.parquet` and `sweep_cp_sat.parquet`, on the 96
Henn & Wäscher instances. The curve is on the [Pareto chart](pareto.md).

## Modelling choice: order nodes

Both models in the task were built and run; the chart uses **order nodes**.

- **Pick nodes** (one node per pick, all of an order's picks on one vehicle) is the faithful model:
  a vehicle's cost is a travelling-salesman tour through its picks, which is what optimal
  (Ratliff & Rosenthal) routing computes. OR-Tools does find those tours: on small instances its
  tour lengths match the exact router (`tests/test_solvers_ortools.py`). But it can't re-batch.
  Its local search moves one node, or a chain of consecutive nodes, at a time, and moving one pick
  of a multi-pick order breaks the same-vehicle constraint. Started from savings, it returned the
  savings batches in all 384 runs (96 instances x S-shape and largest gap x 1 s and 10 s), so its
  result is exactly savings at 50-1,000x the time. Without the warm start, the default
  first-solution heuristic found no feasible solution within 1 s on a 40-order instance.
  It wasn't too slow to run at 80 orders; it just never changes the batching.
- **Order nodes** (one node per order at its centre of gravity: mean aisle and mean position,
  rounded) is the common practitioner approximation, and the one that actually searches over
  batchings, so it's the curve on the chart.

Both start from the savings solution and run guided local search to the deadline, with integer arc
costs (distances x 10). The solver returns what OR-Tools returns, re-scored. It doesn't fall back
to the savings start when that scores better, since that would turn the baseline into savings.

## Results

Mean % walking distance saved against FCFS (from [pareto.md](pareto.md)):

| Solver | S-shape | Largest gap |
|---|---:|---:|
| OR-Tools, order nodes, 100 ms | 10.1 | 9.3 |
| OR-Tools, order nodes, 1 s | 10.0 | 9.2 |
| OR-Tools, order nodes, 10 s | 10.3 | 9.4 |
| OR-Tools, pick nodes, 1 s and 10 s | 24.4 (= savings) | 20.7 (= savings) |
| Seed (0.6 ms) | 15.2 | 10.6 |
| Savings (11-12 ms) | 24.4 | 20.7 |
| ALNS, 1 s | 27.7 | 23.2 |
| CP-SAT, 1 s | 27.2 | 22.8 |

- **Our solvers beat it by a wide margin.** With order nodes, OR-Tools' batches are 19% longer
  than savings' under S-shape and 15% longer under largest gap (mean per instance, 1 s), worse than
  savings on all 96 instances at 1 s, and worse than seed batching on 83% (S-shape) and 62%
  (largest gap) of them. Across all budgets it beat savings in 5 of 1,344 runs, all on two
  20-order instances at budgets of 500 ms or less (and lost the gain with more time). ALNS at
  100 ms saves 2.4-2.6x as much distance as OR-Tools at 10 s.
- **More time doesn't help.** The curve is flat from 100 ms to 10 s (10.1 to 10.3% under S-shape).
  OR-Tools does improve its own objective: on three 80-order instances it cut it by 30-45% from
  the savings start. But the centre-of-gravity distance isn't the tour length. An order's picks
  spread over several aisles, so two orders with nearby centres can need quite different aisles.
  Minimising the proxy moves away from good batches.
- **It loses most where batching matters most.** The gap to savings grows with instance size
  (S-shape, 1 s: 12.8% at 20 orders, 23.5% at 80) and capacity (15.3% at 45 items, 23.6% at 75):
  the more orders share a tour, the more the proxy's error compounds.
- **Where it doesn't lose:** with pick nodes it ties savings exactly, because it keeps savings'
  batches. Its own tours are as good as optimal routing on small batches, so as a router it's
  sound; it's as a batching method that the routing formulation fails.

## Reproduce

Development instances only (Henn & Wäscher). About 16 minutes on 6 workers.

```bash
cd projects/01-fulfilment-optimisation
B="PYTHONPATH=src python -m fulfilment_optimisation.benchmark"
eval $B --solvers ortools --routers s_shape largest_gap --time-limits 0.1 0.25 0.5 1 2 5 10 \
    --workers 6 --output sweep_ortools.parquet
eval $B --solvers ortools --routers s_shape largest_gap --time-limits 1 10 \
    --param ortools.model=pick_nodes --workers 6 --output ortools_pick_nodes.parquet
PYTHONPATH=src python -m fulfilment_optimisation.report  # adds the curve to the chart and table
```
