# Project 12: Small Transformer from Scratch

**One line:** a decoder-only transformer written and trained from scratch in PyTorch across a size
sweep, with each modern component added as a measured ablation.

**Time box:** ~6 weeks part-time. Range project.

## Headline question

> Does a from-scratch decoder-only transformer, trained across a size sweep, reproduce
> compute-optimal scaling trends on a modest budget?

## Why it matters

Calling an API is easy. Building, training, debugging and scaling the model itself shows depth that
applied work rarely does.

## Data

| Source | What | Access | Licence | Use |
|--------|------|--------|---------|-----|
| An open web or code corpus, e.g. [FineWeb-Edu](https://huggingface.co/datasets/HuggingFaceFW/fineweb-edu) | Pre-training text, tokenised once and reused | Hugging Face download | *Unverified* | Training |

## Scope

**Must have**
- **Models:** 5 sizes from roughly 10M to 125M parameters.
- **Budget:** a single rented GPU node, capped at a fixed dollar figure stated in the write-up.
- **From scratch:** the model, tokenizer pipeline and training loop written in PyTorch. No high-level trainer frameworks.
- **Modern components, added one at a time:** RoPE, RMSNorm, SwiGLU, mixed precision, gradient checkpointing, FlashAttention. Each is logged as an ablation with its measured effect on loss.
- **Scaling:** sweep model size and token count to fit a loss vs compute curve.

**Out of scope:** instruction tuning, RLHF, models above ~150M parameters.

## Milestones

| Weeks | Milestone | Exit criterion |
|-------|-----------|----------------|
| 1–2 | Model + training loop | Overfits a tiny batch; matches a reference implementation's loss |
| 3–4 | Size and data sweep | 5 sizes trained, curves logged |
| 5–6 | Ablations + write-up | Scaling fit, ablation table, lessons learned |

## Deliverables and headline chart

- **Scaling-law plots** (loss vs compute).
- A readable single-repo implementation, training logs, and a write-up.

## Design decisions to write up

- How the sweep was sized to the fixed budget.
- What each modern component bought, from the ablation table.

## Risks and gotchas

- **Compute cost creeps.** Fix the budget up front and size the sweep to it.
- **Bugs masquerade as findings.** Validate against a known reference implementation before any sweep.

## Done when

- [ ] Fitted scaling curve with a reasonable exponent
- [ ] Clean ablation table
- [ ] Everything reproducible from the repo within the stated budget

**Stack:** PyTorch, a rented GPU, Weights & Biases.
