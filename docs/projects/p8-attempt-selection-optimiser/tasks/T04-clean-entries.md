# T04: Clean entries

**Phase:** 1 Data preparation · **Estimate:** 2 h · **Depends on:** T03

## Ask

Deduplicate lifters entered in multiple divisions at one meet, and handle `Place` codes, 4th attempts,
lb→kg rounding artefacts and approximate ages.

## Why

Duplicate entries double-count attempts, 4th attempts don't count towards totals, and unit artefacts
break the 2.5 kg increment logic the optimiser relies on.

## How

- Dedupe: one row per (`Name`, meet); document which division is kept.
- `Place`: map DQ/DD/NS/Guest to explicit flags and decide per code whether the attempts are usable
  for the make-probability model and whether the entry counts for placing. Record each decision.
- 4th attempts: keep in a separate column; exclude from totals and from the training set.
- lb→kg: detect weights that are lb conversions rather than kg increments, then flag or snap them.
  Confirm the pattern on the data before choosing.
- Ages ending `.5` are approximate; keep a flag.

## Plan

- [ ] Dedupe function
- [ ] Place-code handling
- [ ] 4th-attempt split
- [ ] lb→kg detection
- [ ] Age flag
- [ ] A fixture test for each

## Acceptance criteria

- [ ] No (`Name`, meet) pair appears twice after cleaning
- [ ] Totals recomputed from best attempts 1–3 match `TotalKg` for ≥ 99% of rows, with mismatches explained
- [ ] Each rule has a fixture test
- [ ] Row counts before/after each step are logged
