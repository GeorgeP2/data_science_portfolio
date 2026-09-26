# T19: TF-IDF + logistic regression baseline

**Phase:** 5 Fine-tune vs prompt · **Estimate:** 1 h · **Depends on:** T18

## Ask

Train and score a TF-IDF + logistic regression classifier as option (a).

## Why

The baseline sets the bar. If it gets 90%, that's the story, and the write-up has to say so.

## How

- Character + word n-gram TF-IDF (jargon like `"PASS COMM"` suits char n-grams), plus one-hot
  event type; class-weighted logistic regression. Tune C on validation.
- Measure latency per request and cost (≈ compute only).

## Plan

- [ ] Pipeline
- [ ] Tune on validation
- [ ] Score on test: macro-F1, per-class F1, p50/p95 latency

## Acceptance criteria

- [ ] Macro-F1 on test is reported with per-class breakdown
- [ ] Latency measured on the same hardware notes as the other options
- [ ] Deterministic with the configured seed
