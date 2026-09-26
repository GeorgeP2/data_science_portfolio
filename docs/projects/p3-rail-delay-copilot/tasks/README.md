# P3 tasks

Atomic tasks for the [Rail Delay Copilot](../brief.md). One file per task, each with
**Ask / Why / How / Plan / Acceptance criteria**.

| # | Task | Phase | Est. | Depends on |
|---|------|-------|------|------------|
| [T01](T01-scaffold-project.md) | Scaffold the project | 0 Setup | 1 h | none |
| [T02](T02-download-delay-data.md) | Download delay data + mirror a sample | 0 Setup | 2 h | T01 |
| [T03](T03-download-rulebook-docs.md) | Download DAPR, PGDs and rulings | 0 Setup | 1 h | T01 |
| [T04](T04-duckdb-ingestion.md) | Load periods into DuckDB | 1 Ingestion | 2 h | T02 |
| [T05](T05-dedup-and-deemed-minutes.md) | Dedup incidents + deemed minutes | 1 Ingestion | 2 h | T04 |
| [T06](T06-schema-description.md) | Schema description for text-to-SQL | 1 Ingestion | 1 h | T05 |
| [T07](T07-rulebook-chunking.md) | Section-aware rulebook chunking | 2 Retrieval | 3 h | T03 |
| [T08](T08-hybrid-index.md) | Hybrid BM25 + embedding index | 2 Retrieval | 2 h | T07 |
| [T09](T09-reranking-and-citations.md) | Reranking and cited rules answers | 2 Retrieval | 2 h | T08 |
| [T10](T10-text-to-sql-tool.md) | Text-to-SQL tool with validation | 3 Agent | 3 h | T06 |
| [T11](T11-agent-routing.md) | Agent: routing, both tools, refusal | 3 Agent | 3 h | T09, T10 |
| [T12](T12-mcp-server.md) | MCP server + demo GIF | 3 Agent | 2 h | T09, T10, T20 |
| [T13](T13-cost-latency-tracking.md) | Cost and latency dashboard | 3 Agent | 2 h | T11 |
| [T14](T14-golden-set.md) | Golden evaluation set (~150) | 4 Evaluation | 4 h | T05, T07 |
| [T15](T15-sql-and-rag-scorers.md) | SQL + citation-grounded scorers | 4 Evaluation | 2 h | T11, T14 |
| [T16](T16-llm-judge-calibration.md) | LLM judge + calibration | 4 Evaluation | 2 h | T14, T15 |
| [T17](T17-make-eval-and-ci.md) | `make eval` + CI regression gate | 4 Evaluation | 2 h | T13, T15, T16 |
| [T18](T18-classification-dataset.md) | Incident classification dataset | 5 Fine-tune vs prompt | 1.5 h | T05 |
| [T19](T19-tfidf-baseline.md) | TF-IDF + logistic regression baseline | 5 Fine-tune vs prompt | 1 h | T18 |
| [T20](T20-frontier-few-shot.md) | Frontier API model, few-shot | 5 Fine-tune vs prompt | 2 h | T07, T18 |
| [T21](T21-lora-fine-tune.md) | LoRA / QLoRA fine-tune | 5 Fine-tune vs prompt | 4 h | T18 |
| [T22](T22-fine-tune-vs-prompt-results.md) | Results table + recommendation | 5 Fine-tune vs prompt | 2 h | T19–T21 |
| [T23](T23-failure-mode-analysis.md) | Failure-mode analysis | 6 Write-up | 2 h | T17, T22 |
| [T24](T24-design-decisions-writeup.md) | Design decisions write-up | 6 Write-up | 2 h | T07, T16, T17, T22 |
| [T25](T25-readme.md) | Project README | 6 Write-up | 1.5 h | T12, T17, T22–T24 |
| [T26](T26-stretch-hf-space-demo.md) | *Stretch:* Hugging Face Space demo | Stretch | 3 h | T11, T25 |
| [T27](T27-stretch-injection-guardrails.md) | *Stretch:* prompt-injection guardrails | Stretch | 3 h | T11, T17 |

**Total:** ~52 h must-have against a ~40 h time box (stretch adds ~6 h). If it runs over, cut in
this order:

1. T13: print cost/latency tables from `make eval` instead of a dashboard (−1.5 h)
2. T14: ~100 golden questions instead of ~150 (−1.5 h)
3. T09: drop the reranker, keep hybrid retrieval + citations (−1 h)
4. T20: one API model instead of two (−0.5 h)
5. T21: one model, one training run, no hyperparameter search (−1 h)

That still leaves ~46 h. Closing the rest means either moving the fine-tune vs prompt experiment
(T18–T22) into its own time box or extending this one; decide at the end of week 9.

## Mapping to "Done when"

| Brief criterion | Tasks |
|-----------------|-------|
| `make eval` prints accuracy / cost / latency tables, and CI runs it | T13–T17 |
| MCP server works from Claude Desktop or Claude Code, with a demo GIF in the README | T12, T25 |
| Fine-tune vs prompt results table with a written recommendation | T18–T22 |
| Failure-mode write-up | T23 |
