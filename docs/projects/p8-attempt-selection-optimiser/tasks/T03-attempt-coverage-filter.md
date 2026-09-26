# T03: Filter to meets with full attempt data and report coverage

**Phase:** 1 Data preparation · **Estimate:** 2 h · **Depends on:** T02

## Ask

Keep only meets that report all attempts, and report how much of the data survives by federation,
year and equipment.

## Why

Many meets only report best lifts, so attempt-level modelling needs a filter. The brief asks for
coverage to be reported because the filter shapes which lifters the model represents.

## How

- Define "full attempts" at meet level (e.g. every lifter has `Squat1Kg…Deadlift3Kg` populated unless
  they didn't take the attempt). Write the rule down before applying it.
- Coverage table: rows and meets before/after, by federation, year and equipment.

## Plan

- [ ] Inspect missingness patterns in the attempt columns
- [ ] Write and document the meet-level rule
- [ ] Implement the filter as a tested function
- [ ] Coverage table and plot into `reports/figures/`

## Acceptance criteria

- [ ] Filter rule is documented in a docstring
- [ ] Unit test on a fixture with full, partial and best-only meets
- [ ] Coverage table is saved and reproducible from one command
