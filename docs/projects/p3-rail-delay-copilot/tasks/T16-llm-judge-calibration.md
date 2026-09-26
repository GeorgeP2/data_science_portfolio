# T16: LLM-as-judge with calibration against my labels

**Phase:** 4 Evaluation · **Estimate:** 2 h · **Depends on:** T14, T15

## Ask

Add an LLM judge for answer correctness on rules and mixed questions, and measure its agreement with
my own labels.

## Why

Free-text answers need semantic scoring. A judge is only trustworthy if its agreement with a human
is measured; this is a design decision to write up.

## How

- Judge prompt with a rubric (correct / partially correct / wrong + reason), reference answer and
  cited sections in context. Judge model ID in config, ideally different from the agent's model.
- Hand-label ~50 agent answers blind, then compare: accuracy and Cohen's kappa.
- Iterate the rubric on a dev half, report agreement on the other half.

## Plan

- [ ] Judge prompt and rubric
- [ ] Hand-label ~50 answers
- [ ] Agreement metrics on dev / test halves
- [ ] Short note on disagreements

## Acceptance criteria

- [ ] Agreement (accuracy and kappa) is reported on labels not used to tune the rubric
- [ ] Judge outputs are cached so re-runs are free
- [ ] Disagreement examples are saved for the failure-mode write-up
