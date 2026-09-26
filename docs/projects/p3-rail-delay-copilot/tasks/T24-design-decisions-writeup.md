# T24: Design decisions write-up

**Phase:** 6 Write-up · **Estimate:** 2 h · **Depends on:** T07, T16, T17, T22

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section; it's where judgement is visible.

## How

One subsection each, backed by eval numbers:
1. When to use SQL, retrieval or both, and how routing errors show up in the evals.
2. Chunking a legal-style rulebook, including cross-references.
3. Judge calibration: agreement between my labels and the LLM judge.
4. Why the baseline matters (T19 vs the others).

## Plan

- [ ] Draft the four subsections
- [ ] Link each claim to a table, figure or test

## Acceptance criteria

- [ ] All four decisions covered, each with the alternative considered and why it lost
- [ ] Every quantitative claim points to a reproducible result
