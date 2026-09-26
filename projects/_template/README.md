# {{title}}

> **Category:** {{category}} · **Status:** 🚧 In progress

## Problem

_What question is being answered, and why does it matter? Who would use the result?_

## Data

| Source | Rows × Cols | Licence | Notes |
|--------|-------------|---------|-------|
| _link_ | | | |

Raw data lives in `data/raw/` (git-ignored). Describe how to obtain it here so the project is reproducible.

## Approach

1. **EDA** — `notebooks/01_eda.ipynb`
2. **Features** — `src/{{package}}/features.py`
3. **Modelling** — `src/{{package}}/train.py`
4. **Evaluation** — metrics written to `outputs/metrics.json`, figures to `reports/figures/`

## Results

| Model | Metric | Score |
|-------|--------|-------|
| Baseline | | |

_Key figure(s):_

<!-- ![](reports/figures/example.png) -->

## Key takeaways

- …

## Reproduce

```bash
# from the repo root, with the venv active
cd projects/{{slug}}
PYTHONPATH=src python -m {{package}}.train
pytest
```

## Skills demonstrated

- …
