# T09: Reranking and cited rules answers

**Phase:** 2 Retrieval · **Estimate:** 2 h · **Depends on:** T08

## Ask

Add a reranker over the fused candidates, and a `search_rules` step that answers with section citations.

## Why

Reranking lifts precision in the few chunks the LLM sees. Citations make rules answers checkable and
are what the RAG eval scores.

## How

- Cross-encoder reranker (model in config) over the top-N fused candidates; optional expansion with
  cross-referenced sections from T07 (config flag).
- Answer prompt requires citations like `[DAPR §x.y]` and says to decline when the chunks don't
  cover the question.
- Answers note that DAPR is the current edition while the delay data ends Dec 2023.

## Plan

- [ ] Reranker
- [ ] Cross-reference expansion behind a flag
- [ ] `search_rules` returning answer + citations
- [ ] Re-run the T08 retrieval check

## Acceptance criteria

- [ ] Recall@5 with reranking is reported next to T08's numbers and is not worse
- [ ] Every rules answer includes at least one citation that exists in the index
- [ ] On 5 hand-made unsupported questions, it declines rather than guesses
