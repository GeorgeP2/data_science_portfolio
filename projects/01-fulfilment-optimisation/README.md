# Fulfilment Optimisation

> **Category:** MLOps & Deployment · **Status:** 🚧 In progress

## Problem

> For a manual picker-to-parts warehouse, how much walking distance can batching and routing
> optimisation save compared with first-come-first-served greedy batching, and what does each
> extra millisecond of solve time buy?

An order-batching and pick-path optimisation API that beats a greedy baseline within a hard latency
budget, benchmarked against published academic instances so the claims can be checked.

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

_TBC._

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
cd projects/01-fulfilment-optimisation
PYTHONPATH=src python -m fulfilment_optimisation.download   # benchmark instances → data/raw/
pytest
```

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

The image is 76 MB compressed (347 MB unpacked). It contains no benchmark data: its ignore file
lets in only the code and `config.yaml`.

## Skills demonstrated

- …
