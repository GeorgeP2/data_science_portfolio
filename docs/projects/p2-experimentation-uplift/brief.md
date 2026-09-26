# Project 2: Experimentation & Uplift Case Study

**One line:** a rigorous re-analysis of a real 344k-person randomised field experiment. It covers
CUPED, cluster-robust inference, heterogeneous effects and uplift targeting, plus sequential testing
on 78 real e-commerce A/B tests. It ends with a decision memo.

**Time box:** weeks 13–18 (~40 h).

## Headline questions

> 1. **Targeting:** given a fixed budget of mailings, which people should be treated, and how
>    many extra outcomes does uplift targeting buy over random or "treat everyone" targeting?
> 2. **Speed:** on real e-commerce experiments, how much sooner could decisions be made with
>    CUPED-style variance reduction and valid sequential tests than with fixed-horizon t-tests
>    (while keeping false positives controlled)?

## Why this data is different

Criteo Uplift is in every uplift tutorial. Instead:
- **Gerber, Green & Larimer (2008)** is a landmark field experiment: household-randomised
  mailings with four treatment arms, individual outcomes and several years of pre-treatment history.
  That history is exactly what CUPED needs. Econometrics papers use it all the time; DS portfolios almost never do.
- **The ASOS Digital Experiments Dataset** is 78 real online experiments from a UK fashion retailer,
  with cumulative per-arm statistics at every checkpoint. That makes it ideal for showing why peeking
  inflates false positives and how sequential methods fix it.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| [GGL 2008 social pressure experiment](https://doi.org/10.60600/YU/CGMWNW) (Yale ISPS Dataverse) | 344,084 individuals: `treatment` (control + 4 mailings), `voted`, prior participation `g2000…p2004`, `sex`, `yob`, `hh_id`, `hh_size`, `cluster` | Direct download, no login (~20 MB) | CC0 |
| [ASOS Digital Experiments Dataset](https://osf.io/64jsb/) (Liu et al., 2021) | 78 experiments, 24k rows of cumulative sufficient statistics (count, mean, variance per arm) at 12-hour or daily checkpoints | Direct download from OSF (~1 MB parquet) | CC BY 4.0 |
| *Optional:* Lenta uplift (via `scikit-uplift`) | ~687k retail customers, 190+ features | Direct download | *Unverified*: use for internal stress tests only |

## Scope

**Part A: Field experiment (GGL)**
- **Balance and randomisation checks:** SRM (sample-ratio mismatch) and covariate balance.
- **ATE per arm** with standard errors clustered on household, which shows why naive standard errors are wrong.
- **CUPED / regression adjustment:** use prior participation to cut variance, and report the effective sample-size gain.
- **Heterogeneous effects:** T-learner, X-learner and causal forest (EconML), plus a DR-learner as a check.
- **Qini / uplift curves** with bootstrap confidence intervals, showing the lift from targeting vs random at a fixed budget.
- A **power calculator** (small CLI/Streamlit) built on the variance estimates from the data.

**Part B: Sequential testing (ASOS)**
- Simulate "peeking" on A/A-like null comparisons to show the inflated false-positive rate.
- Implement mSPRT / always-valid confidence sequences and a group-sequential design (O'Brien–Fleming).
- Report time-to-decision vs fixed-horizon across the 78 experiments.
- Meta-analysis of effect-size distributions, i.e. what a typical e-commerce effect looks like, which informs sensible minimum detectable effects (MDEs).

**Deliverable:** a two-page **decision memo**, "who should we treat, and what's it worth?", with cost per mailing as a parameter. It should read like something a product lead could act on.

**Stretch:** Bayesian A/B analysis (PyMC) of the same arms; difference-in-differences or synthetic control on a public UK policy change.

**Out of scope:** building an experimentation platform.

## Design decisions to write up

- Clustered vs individual randomisation, and what goes wrong if you ignore it.
- How to choose between the CUPED covariates and why using post-treatment variables is a trap.
- Evaluating uplift models when there's no ground truth per individual.
- Sequential methods: the trade-off between power and flexibility.

## Risks and gotchas

- **Few features in GGL** (~8), so uplift curves will be modest. That's an honest finding, not a failure. Use Lenta to show what richer features do.
- **GGL columns to fix:** `g2004` is constant (the sample was restricted to 2004 voters), so drop it; and re-derive household-level aggregates like `p2004_mean` within cross-validation folds to avoid leakage.
- **ASOS data is aggregate-only.** User-level CUPED isn't possible on it; that part lives in Part A.
- **Framing:** keep the GGL write-up neutral and methodological. The interest is the experimental design, not the politics.

## Done when

- [ ] Notebook-free reproducible pipeline: `make analysis` → figures + memo
- [ ] Qini chart and sequential-testing chart in the README
- [ ] Power calculator usable by someone else
- [ ] Decision memo in `reports/`
