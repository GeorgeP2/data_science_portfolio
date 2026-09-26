# T21: Design decisions write-up

**Phase:** 5 Write-up · **Estimate:** 2 h · **Depends on:** T10, T13, T15

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section. It's where judgement is visible, not just code.

## How

One short subsection each, backed by numbers from the backtests where possible:
1. Choosing the backtest window, and how a model gets promoted.
2. Calibration vs sharpness, and why pinball loss alone isn't enough.
3. When partial pooling helps (sparse groups) and when it doesn't.
4. The cost of the Bayesian model: sampling time vs benefit, and the use of VI.

Also note the data caveats: embedded solar/wind are modelled, not metered; the LCL hierarchy source
(T05); actual vs forecast weather in backtests (T06).

## Plan

- [ ] Draft the four subsections
- [ ] Data caveats paragraph
- [ ] Link each claim to a figure, table or test

## Acceptance criteria

- [ ] All four decisions are covered, each with the alternative considered and why it lost
- [ ] Every quantitative claim points to a reproducible result
