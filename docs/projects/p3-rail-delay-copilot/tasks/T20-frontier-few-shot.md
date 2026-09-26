# T20: Frontier API model, few-shot with the code table

**Phase:** 5 Fine-tune vs prompt · **Estimate:** 2 h · **Depends on:** T07, T18

## Ask

Classify incidents with a frontier API model, few-shot, with the DAPR cause-code table in context,
as option (c).

## Why

The prompting side of headline question 2, and the first implementation behind the
`classify_incident` MCP tool.

## How

- Prompt: code table from T07 (top-N codes + "other"), a handful of examples per code from train,
  structured output constrained to valid codes.
- Model IDs in config; run at least one large and one small model (e.g. `claude-sonnet-5` and
  `claude-haiku-4-5-20251001`) to show the cost/accuracy spread. Use prompt caching for the
  shared code table.
- Score on the fixed test subset; record tokens → cost per 1k requests, p50/p95 latency.

## Plan

- [ ] Prompt with code table and examples
- [ ] Structured output + validation
- [ ] Run on test subset with caching of responses
- [ ] Record F1, cost, latency

## Acceptance criteria

- [ ] Macro-F1, cost per 1k requests and p50/p95 latency are reported per model
- [ ] Every output is a valid code or "other"
- [ ] Re-running uses cached responses (no repeat spend)
