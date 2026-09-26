# T18: Design decisions write-up

**Phase:** 6 Write-up · **Estimate:** 2 h · **Depends on:** T08, T13, T15, T16

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section; it's where judgement is visible, not just code.

## How

One short subsection each, backed by numbers where possible:
1. Why two stages: latency and compute per stage (T16 breakdown).
2. Negative sampling for the two-tower model (T08 comparison).
3. What recommended events do to offline evaluation: exposure bias (T13, T14).
4. Cache invalidation and freshness vs latency (T15).

Mention sequence transformers (SASRec etc.) as out of scope, with one line on why.

## Plan

- [ ] Draft the four subsections
- [ ] Link each claim to a figure, table or test

## Acceptance criteria

- [ ] All four decisions covered, each with the alternative considered and why it lost
- [ ] Every quantitative claim points to a reproducible result
