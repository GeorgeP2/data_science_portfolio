# Data

Nothing under `raw/` is committed. Fetch it from the project folder with:

```bash
PYTHONPATH=src python -m fulfilment_optimisation.download            # everything (~4 GB on disk)
PYTHONPATH=src python -m fulfilment_optimisation.download henn_waescher
PYTHONPATH=src python -m fulfilment_optimisation.download kit
```

Every file is checked against a SHA-256 pinned in `src/fulfilment_optimisation/download.py`.
Re-running skips files that are already present and verified. A corrupted file stops the run with
an error; delete it to fetch it again. An interrupted download leaves a `.part` file, and the next
run resumes it.

Henn & Wäscher and Foodmart state no licence. Their files are fetched from the authors' pages
rather than redistributed; don't commit or re-host anything in `raw/`. KIT is CC BY 4.0 but too large
to commit.

## Henn & Wäscher instances → `raw/henn_waescher/`

- **Source:** [OPTSICOM order batching and sequencing page](https://grafo.etsii.urjc.es/optsicom/obsp.html)
  (`obsp_instances.zip`, 0.4 MB zipped, 2.7 MB unpacked, plus two results workbooks in `results/`).
- **Contents:** 96 instances in two folders of 48 (`MTCR_05_06_07`, `MTCR_055_065_075`). Each
  instance file (`<setting>l-<orders>-<capacity>-0.txt`) has a matching `sett<setting>.txt` layout
  file.
  - Layout: 10 aisles, 45 cells per aisle side (90 locations per aisle), depot bottom left,
    class-based (ABC) storage.
  - 20, 40, 60 or 80 orders; picker capacity 45 or 75 items.
  - Each order has a due date. MTCR sets how tight the due dates are.
  - The page text says 40–100 orders and capacity 30–75, but the files don't match that; the
    numbers above come from the files.
- **Citation:** Henn, S., Wäscher, G. (2012). Tabu search heuristics for the order batching problem
  in manual order picking systems. *EJOR* 222(3), 484–494. Due dates were added by Henn & Schmid
  (2013) and Menéndez et al. (2017).
- **Licence:** not stated.
- **Published values:** `../references/henn_waescher_best_known.csv` (total tardiness per instance;
  see `../references/README.md`).

## Foodmart instances → `raw/foodmart/`

- **Source:** [Arbex Valle order picking instances](https://homepages.dcc.ufmg.br/~arbex/orderpicking.html)
  (1.2 MB).
- **Contents:**
  - Four warehouse layouts (`warehouse_{8,16}_{0,1}_3_1560`: 8 or 16 aisles, 1 or 2 blocks).
  - The product list and product-to-slot map (1,560 SKUs).
  - `orders/`: 141 instances of 5–75 orders (47 each for d5, d10 and d20).
  - `large_instances/`: 50–5,000 orders.
  - `instanceFilesDescription.txt` documents the format.
  - The page's links to `warehouse_8_1_3_1560`, `productsDB_1560_list` and
    `productsDB_1560_locations` return 404. The same files are served with a `.txt` suffix, and the
    script saves them under the documented names.
- **Citation:** Valle, C. A., Beasley, J. E., da Cunha, A. S. (2017). Optimally solving the joint
  order batching and picker routing problem. *EJOR* 262(3), 817–834.
- **Licence:** not stated. The order data derives from the Pentaho Foodmart sample database.
- **Published values:** not transcribed yet. The optimal values are in the paper's tables; this is
  deferred to the Foodmart parser.

## KIT benchmark suite → `raw/kit/`

- **Source:** [KIT RADAR, Benchmark Instances for Manual Warehouse Order Picking](https://radar.kit.edu/radar/en/dataset/mwsv59v8sk9sqaan)
  (DOI [10.35097/mwsv59v8sk9sqaan](https://doi.org/10.35097/mwsv59v8sk9sqaan), version 1, published
  2026-04-29).
- **Size:** one 2.0 GB BagIt tar. The script keeps it (so re-runs can verify it) and unpacks only
  the nested `Instances.tar` into `raw/kit/Instances/` (1.9 GB, 13,438 files). Allow ~4 GB.
- **Contents** (`Instances/Readme.txt` documents the format):
  - `Data_input/{OFAT,LHS}/`: 104 layouts as pickled NetworkX graphs (`Layout/*.pkl`) and storage
    assignments as JSON (`Storage_assignment/`). Rectangular, parallel aisles, cross aisles top and
    bottom, depot at (0, 0), distances in abstract length units.
  - `Orders/OFAT/`: a `Standard_case/` plus seven folders that each vary one factor (article
    distribution, due date, layout, number of orders, articles per order, stochasticity, storage
    policy); 3,207 JSON instances, each one shift.
  - `Orders/LHS/`: 100 Latin hypercube parameter sets × 100 replications (10,000 JSON instances).
  - `Results/`: example solutions (routing and waiting heuristics) for selected instances.
  - Loading a layout means `pickle.load`, which runs code from the file. Only load the pinned,
    checksum-verified copy.
- **Citation:** Barlang, M., Lehmann, T., Furmans, K. (2026). *Benchmark Instances for Manual
  Warehouse Order Picking.* Karlsruhe Institute of Technology, RADAR.
  https://doi.org/10.35097/mwsv59v8sk9sqaan
- **Licence:** [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Anything derived from it
  (the generator calibration) must credit the citation above.
