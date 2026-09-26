# T27: Design decisions write-up

**Phase:** 7 Write-up · **Estimate:** 2 h · **Depends on:** T12, T20, T23

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section; it's where judgement is visible, not just code.

## How

One short subsection each, backed by numbers from the harness where possible:
1. CP-SAT vs MIP: where each wins, and why CP-SAT here.
2. Anytime algorithms and returning a solution under a deadline.
3. Generator validity (summarise T20).
4. API contract: infeasible and oversized requests.

## Plan

- [ ] Draft the four subsections
- [ ] Link each claim to a figure, table or test

## Acceptance criteria

- [ ] All four decisions covered, each with the alternative considered and why it lost
- [ ] Every quantitative claim points to a reproducible result
