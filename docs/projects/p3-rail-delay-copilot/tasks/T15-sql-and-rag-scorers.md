# T15: SQL execution accuracy and citation-grounded scoring

**Phase:** 4 Evaluation · **Estimate:** 2 h · **Depends on:** T11, T14

## Ask

Implement the deterministic scorers: execution accuracy for SQL answers, citation grounding for rules
answers, and routing/refusal correctness for every question.

## Why

Deterministic scores are cheap, reproducible and trustworthy. The LLM judge (T16) only covers what
they can't.

## How

- SQL: compare result sets (order-insensitive unless the question asks for ordering, numeric tolerance).
- Rules: cited sections ⊆ retrieved chunks, and overlap with the reference sections.
- Routing: tools called vs the question type; refusals on unanswerable questions.

## Plan

- [ ] Result-set comparison
- [ ] Citation checks
- [ ] Routing / refusal checks
- [ ] Unit tests with hand-made cases

## Acceptance criteria

- [ ] Each scorer has unit tests including known pass and fail cases
- [ ] Scores are reported per question type
- [ ] Routing errors are counted separately from answer errors
