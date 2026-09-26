# T19: Design decisions write-up

**Phase:** 5 Write-up · **Estimate:** 2 h · **Depends on:** T10, T13, T16

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section; it's where judgement shows, not just code.

## How

One short subsection each, backed by measured numbers:
1. Where state lives (in-process vs Redis vs a stream processor) and failure recovery (T13).
2. Event time vs processing time; handling out-of-order events (T11, T12).
3. Why AUC isn't the business metric (T10).
4. Latency budget breakdown: deserialisation, feature lookup, inference, publish (T16).

## Plan

- [ ] Draft the four subsections
- [ ] Link each claim to a figure, table or test

## Acceptance criteria

- [ ] All four decisions covered, each with the alternative considered and why it lost
- [ ] The latency breakdown adds up to the measured p50/p99
- [ ] Every quantitative claim points to a reproducible result
