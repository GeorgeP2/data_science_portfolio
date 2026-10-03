# Distance results against Henn & Wäscher (2010)

Generated from the benchmark results. To regenerate, from the project folder:

```bash
PYTHONPATH=src python -m fulfilment_optimisation.benchmark  # 1 s grid, about 1.5 min
PYTHONPATH=src python -m fulfilment_optimisation.benchmark --solvers savings alns \
    --time-limits 10 60 --orders 40 60 80 --param alns.max_iterations=100000000 \
    --output runs_long.parquet  # about 20 min with 10 workers
PYTHONPATH=src python -m fulfilment_optimisation.published \
    --runs runs.parquet runs_long.parquet
```

Improvement of the average tour length over C&W(ii) savings, per class, against the published `abhc` (ABHC*, their best method; FEMM 07/2010 Tables 9.2 and 9.5). Pass if ours is no more than 1 percentage point below. Different instances from the same generator, so the 95% bootstrap interval shows the sampling noise in our class means.

## alns, 1 s (6/12 classes within tolerance)

| Routing | Orders | Capacity | Instances | Ours % (95% CI) | Published % | Diff (pp) | |
|---|---:|---:|---:|---|---:|---:|---|
| largest_gap | 40 | 45 | 12 | 3.9 (3.2 to 4.6) | 3.8 | +0.1 | ✅ |
| largest_gap | 40 | 75 | 12 | 6.0 (4.8 to 7.2) | 6.1 | -0.1 | ✅ |
| largest_gap | 60 | 45 | 12 | 3.5 (2.4 to 4.6) | 3.7 | -0.2 | ✅ |
| largest_gap | 60 | 75 | 12 | 2.2 (1.4 to 3.1) | 6.1 | -3.9 | ❌ |
| largest_gap | 80 | 45 | 12 | 0.6 (0.2 to 1.2) | 3.7 | -3.1 | ❌ |
| largest_gap | 80 | 75 | 12 | 0.8 (0.4 to 1.4) | 5.8 | -5.0 | ❌ |
| s_shape | 40 | 45 | 12 | 6.2 (4.6 to 8.0) | 5.3 | +0.9 | ✅ |
| s_shape | 40 | 75 | 12 | 6.2 (4.6 to 8.0) | 5.8 | +0.4 | ✅ |
| s_shape | 60 | 45 | 12 | 5.0 (4.1 to 6.0) | 4.4 | +0.6 | ✅ |
| s_shape | 60 | 75 | 12 | 3.9 (2.6 to 5.3) | 5.4 | -1.5 | ❌ |
| s_shape | 80 | 45 | 12 | 1.5 (0.9 to 2.1) | 4.2 | -2.7 | ❌ |
| s_shape | 80 | 75 | 12 | 1.3 (0.7 to 2.0) | 4.5 | -3.2 | ❌ |

## alns, 10 s (12/12 classes within tolerance)

| Routing | Orders | Capacity | Instances | Ours % (95% CI) | Published % | Diff (pp) | |
|---|---:|---:|---:|---|---:|---:|---|
| largest_gap | 40 | 45 | 12 | 3.9 (3.2 to 4.6) | 3.8 | +0.1 | ✅ |
| largest_gap | 40 | 75 | 12 | 6.2 (4.9 to 7.4) | 6.1 | +0.1 | ✅ |
| largest_gap | 60 | 45 | 12 | 4.6 (3.9 to 5.3) | 3.7 | +0.9 | ✅ |
| largest_gap | 60 | 75 | 12 | 5.9 (5.0 to 6.9) | 6.1 | -0.2 | ✅ |
| largest_gap | 80 | 45 | 12 | 4.1 (3.4 to 4.8) | 3.7 | +0.4 | ✅ |
| largest_gap | 80 | 75 | 12 | 4.9 (4.0 to 5.8) | 5.8 | -0.9 | ✅ |
| s_shape | 40 | 45 | 12 | 6.3 (4.8 to 8.0) | 5.3 | +1.0 | ✅ |
| s_shape | 40 | 75 | 12 | 6.5 (5.1 to 8.3) | 5.8 | +0.7 | ✅ |
| s_shape | 60 | 45 | 12 | 6.4 (5.6 to 7.2) | 4.4 | +2.0 | ✅ |
| s_shape | 60 | 75 | 12 | 7.3 (6.1 to 8.2) | 5.4 | +1.9 | ✅ |
| s_shape | 80 | 45 | 12 | 5.7 (4.9 to 6.5) | 4.2 | +1.5 | ✅ |
| s_shape | 80 | 75 | 12 | 6.7 (5.4 to 7.8) | 4.5 | +2.2 | ✅ |

## alns, 60 s (12/12 classes within tolerance)

| Routing | Orders | Capacity | Instances | Ours % (95% CI) | Published % | Diff (pp) | |
|---|---:|---:|---:|---|---:|---:|---|
| largest_gap | 40 | 45 | 12 | 4.0 (3.3 to 4.9) | 3.8 | +0.2 | ✅ |
| largest_gap | 40 | 75 | 12 | 6.2 (4.9 to 7.4) | 6.1 | +0.1 | ✅ |
| largest_gap | 60 | 45 | 12 | 4.8 (4.2 to 5.5) | 3.7 | +1.1 | ✅ |
| largest_gap | 60 | 75 | 12 | 6.1 (5.3 to 6.9) | 6.1 | +0.0 | ✅ |
| largest_gap | 80 | 45 | 12 | 4.3 (3.6 to 5.1) | 3.7 | +0.6 | ✅ |
| largest_gap | 80 | 75 | 12 | 5.9 (5.2 to 6.6) | 5.8 | +0.1 | ✅ |
| s_shape | 40 | 45 | 12 | 6.3 (4.8 to 8.0) | 5.3 | +1.0 | ✅ |
| s_shape | 40 | 75 | 12 | 6.8 (5.3 to 8.9) | 5.8 | +1.0 | ✅ |
| s_shape | 60 | 45 | 12 | 6.5 (5.7 to 7.4) | 4.4 | +2.1 | ✅ |
| s_shape | 60 | 75 | 12 | 7.4 (6.4 to 8.3) | 5.4 | +2.0 | ✅ |
| s_shape | 80 | 45 | 12 | 6.1 (5.3 to 6.8) | 4.2 | +1.9 | ✅ |
| s_shape | 80 | 75 | 12 | 7.4 (6.2 to 8.6) | 4.5 | +2.9 | ✅ |

## cp_sat, 1 s (3/12 classes within tolerance)

| Routing | Orders | Capacity | Instances | Ours % (95% CI) | Published % | Diff (pp) | |
|---|---:|---:|---:|---|---:|---:|---|
| largest_gap | 40 | 45 | 12 | 3.3 (2.5 to 4.2) | 3.8 | -0.5 | ✅ |
| largest_gap | 40 | 75 | 12 | 4.3 (3.0 to 5.5) | 6.1 | -1.8 | ❌ |
| largest_gap | 60 | 45 | 12 | 1.3 (0.5 to 2.1) | 3.7 | -2.4 | ❌ |
| largest_gap | 60 | 75 | 12 | 1.5 (0.8 to 2.3) | 6.1 | -4.6 | ❌ |
| largest_gap | 80 | 45 | 12 | 0.5 (0.1 to 1.0) | 3.7 | -3.2 | ❌ |
| largest_gap | 80 | 75 | 12 | 1.1 (0.6 to 1.7) | 5.8 | -4.7 | ❌ |
| s_shape | 40 | 45 | 12 | 5.4 (3.5 to 7.3) | 5.3 | +0.1 | ✅ |
| s_shape | 40 | 75 | 12 | 5.6 (4.1 to 7.4) | 5.8 | -0.2 | ✅ |
| s_shape | 60 | 45 | 12 | 2.3 (1.4 to 3.3) | 4.4 | -2.1 | ❌ |
| s_shape | 60 | 75 | 12 | 2.9 (2.1 to 3.7) | 5.4 | -2.5 | ❌ |
| s_shape | 80 | 45 | 12 | 0.6 (0.2 to 1.1) | 4.2 | -3.6 | ❌ |
| s_shape | 80 | 75 | 12 | 1.0 (0.5 to 1.5) | 4.5 | -3.5 | ❌ |

