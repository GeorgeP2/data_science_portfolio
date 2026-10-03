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
