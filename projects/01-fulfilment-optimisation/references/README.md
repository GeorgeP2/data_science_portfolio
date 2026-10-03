# Published reference values

## `henn_waescher_best_known.csv`

Per-instance **total tardiness** for the 96 order batching and sequencing instances, transcribed
from the two results workbooks on the [OPTSICOM OBSP page](https://grafo.etsii.urjc.es/optsicom/obsp.html)
(`comparative_vs_ils_sshape.xlsx`, `comparative_vs_ils_largest_gap.xlsx`). One row per
instance × routing × method.

These are tardiness values, not walking distances. The sequencing version of the problem adds due
dates, and its objective is total tardiness. No per-instance distance values are published for these
files.

| `method` | What it is | Citation |
|----------|------------|----------|
| `edd` | Earliest-due-date batching (deterministic baseline) | As reported in Menéndez et al. (2017) |
| `ils` | Iterated local search | Henn & Schmid (2013) |
| `gvns` | General variable neighbourhood search (best known on all 96) | Menéndez et al. (2017) |

- Menéndez, B., Bustillo, M., Pardo, E. G., Duarte, A. (2017). General variable neighborhood
  search for the order batching and sequencing problem. *European Journal of Operational Research*
  263(1), 82–93. doi:10.1016/j.ejor.2017.05.001
- Henn, S., Schmid, V. (2013). Metaheuristics for order batching and sequencing in manual order
  picking systems. *Computers & Industrial Engineering* 66, 338–351.

The workbooks number instances 0–95. `instance` maps them to files: ids 0–47 are the `MTCR_05_06_07`
folder and ids 48–95 the `MTCR_055_065_075` folder, each ordered by setting number (the number
before `s` or `l` in the filename). The mapping was checked against each workbook's per-MTCR sheet:
every id's MTCR value, EDD value and GVNS value agree.

### Why the tardiness values aren't used as a check (yet)

The intended check was to reproduce the published EDD tardiness exactly. EDD is deterministic, so
matching it would confirm the parser, distances, routing and timing in one go. The model follows
Henn & Schmid (FEMM working paper 11/2011): a 3-minute setup per tour, travel at the setting files'
`speed_move` (48 LU/min), `speed_pick` (6 items/min, i.e. 10 s per item), EDD batching (sort by due
date, fill tours up to capacity in that order, pick them back to back), and tardiness reported in
seconds.

- **What matches:** the due dates in each file were generated from single-order processing times
  (Henn & Schmid, eq. 6.1). Recovering those times from the due-date range of all 96 instances and
  regressing them on our single-order tour lengths gives a 3.35-minute setup and 50.1 LU/min
  (R² 0.994), against the files' 3 minutes and 48 LU/min. So our geometry, routing and timing
  agree with the instance generator for single orders.
- **What doesn't:** our EDD tardiness is 0.3–0.6× the published values. The ratio falls as the
  order count grows and is lower for S-shape, which suggests the published evaluation used longer
  multi-order tours than ours.
- **Ruled out:** a different travel speed alone (the per-instance fitted speed varies by ±8%, not
  constant), setup times from 0 to 5 minutes, treating the 20 aisle sides as separate aisles,
  first-fit instead of next-fit batching, and sorting due dates in descending order.

Settling this probably needs the full papers (Menéndez et al., 2017; Henn & Schmid, 2013).

## `henn_waescher_2010_improvements.csv`

Each method's improvement of the **average** tour length over C&W(ii) savings, in percent, per
class of orders × capacity × routing. Transcribed from Henn & Wäscher's working paper (FEMM 07/2010,
Tables 9.2 and 9.5; the journal version is Henn & Wäscher, 2012). `tests/test_published.py` checks
the transcription against the tables' printed averages.

| `method` | What it is |
|----------|------------|
| `ls` | C&W(ii) followed by local search |
| `ils1`, `ils2` | Iterated local search variants |
| `ts` | Their best tabu search variant per routing (TS*(SSR), TS*(LGR)) |
| `abhc` | Attribute-based hill climber, ABHC*: their best method, within 0.1–1.4% of optimal where optima are known (Tables 9.3, 9.6) |

These are on their own 40 random instances per class, not on the files above. They come from the
same generator (order sizes 5–25, class-based storage), but with a 0.5 LU depot offset instead of
1 LU. `python -m fulfilment_optimisation.published` compares our improvement over savings with
these values on the shared classes (40/60/80 orders × capacity 45/75).
