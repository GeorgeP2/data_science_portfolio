# T03: Load and clean the GGL data

**Phase:** 1 Field experiment basics · **Estimate:** 1.5 h · **Depends on:** T02

## Ask

Load GGL into a typed DataFrame, apply the fixes the brief lists, and write it to `data/processed/`.

## Why

Every Part A analysis reads this table. The brief flags column issues that would silently bias
results if missed.

## How

- Confirm the row count (344,084) and columns (`treatment`, `voted`, `g2000…p2004`, `sex`, `yob`,
  `hh_id`, `hh_size`, `cluster`) against the codebook.
- Drop `g2004` after confirming it's constant.
- Encode `treatment` as a categorical with control as the reference; derive age from `yob`.
- **Don't** compute household aggregates (e.g. `p2004_mean`) here. They belong inside CV folds (T07).

## Plan

- [ ] Inspect the file and codebook
- [ ] Write `load_ggl() -> DataFrame` with dtypes and fixes
- [ ] Validation checks: row count, one arm per household, no nulls in key columns
- [ ] Write processed parquet
- [ ] Tests on a small fixture

## Acceptance criteria

- [ ] Row count matches 344,084, or the difference is explained
- [ ] `g2004` is shown to be constant and dropped
- [ ] Every household has exactly one treatment arm (asserted)
- [ ] Fixture test runs without raw data
