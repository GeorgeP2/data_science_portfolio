# T21: Design decisions write-up

**Phase:** 4 Pipeline and write-up · **Estimate:** 2 h · **Depends on:** T05, T06, T10, T17

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section; it's where judgement is visible, not just code.

## How

One short subsection each, backed by numbers from the pipeline:
1. Clustered vs individual randomisation, and what goes wrong if you ignore it (T05).
2. Choosing CUPED covariates, and why post-treatment variables are a trap (T06).
3. Evaluating uplift models without per-individual ground truth (T10).
4. Sequential methods: power vs flexibility (T15–T17).

## Plan

- [ ] Draft the four subsections
- [ ] Link each claim to a figure, table or test

## Acceptance criteria

- [ ] All four decisions covered, each with the alternative considered and why it lost
- [ ] Every quantitative claim points to a reproducible result
