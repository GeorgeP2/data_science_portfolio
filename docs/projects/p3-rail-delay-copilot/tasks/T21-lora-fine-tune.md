# T21: LoRA / QLoRA fine-tune of a 1–3B open model

**Phase:** 5 Fine-tune vs prompt · **Estimate:** 4 h · **Depends on:** T18

## Ask

Fine-tune a ~1–3B open model with Hugging Face `peft` to predict the reason code, as option (b).

## Why

The fine-tuning side of headline question 2.

## How

- Pick one open model in the 1–3B range with a licence that allows this use (confirm before
  training). QLoRA if memory requires.
- Frame as generation of the code label (or a classification head); state which.
- Confirm compute first (local GPU / Apple Silicon / rented GPU) and record its hourly cost for the
  cost comparison.
- Train on train, early-stop on validation; score on the full test set and the fixed subset.
- Measure serving latency and cost per 1k requests on stated hardware.

## Plan

- [ ] Choose model and compute; record licence and cost
- [ ] Training script with `peft`, config-driven
- [ ] Train and early-stop
- [ ] Score: macro-F1, latency, cost
- [ ] Save adapter weights outside git; document how to reproduce

## Acceptance criteria

- [ ] Macro-F1 on test is reported alongside T19 and T20
- [ ] Latency and cost per 1k requests are reported with the hardware stated
- [ ] Training is reproducible from config + seed; adapter weights are not committed
