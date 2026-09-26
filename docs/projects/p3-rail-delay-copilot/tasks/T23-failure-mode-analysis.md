# T23: Failure-mode analysis

**Phase:** 6 Write-up · **Estimate:** 2 h · **Depends on:** T17, T22

## Ask

Write a taxonomy of what goes wrong, with examples, across the agent and the classifier.

## Why

A "done when" item. Showing how the system fails is more convincing than a single accuracy number.

## How

- Go through every failed eval question and misclassification sample; tag each with one category,
  e.g. routing error, wrong SQL semantics (dedup / deemed minutes), retrieval miss, unsupported
  citation, over-refusal, under-refusal, rule changed since the data period, jargon misread.
- Count per category; 1–2 concrete examples each with the trace.

## Plan

- [ ] Export failures from the eval run
- [ ] Tag them
- [ ] Count and pick examples
- [ ] Write-up in `results/`

## Acceptance criteria

- [ ] Every failure on the held-out split is tagged
- [ ] Table of categories with counts and share
- [ ] Each category has at least one worked example
- [ ] Top categories each have a proposed fix or an explicit "won't fix" reason
