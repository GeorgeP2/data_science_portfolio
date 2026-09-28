# Project 2: Rail Delay Copilot (RAG + SQL agent with evals)

**One line:** an agent that answers questions about GB rail delays. It chooses between text-to-SQL
over Network Rail's delay attribution records and retrieval over the industry rulebook that governs
attribution. It ships with an evaluation suite and a fine-tune vs prompt experiment.

**Time box:** weeks 7–12 (~40 h). This is the priority LLM project.

## Headline questions

> 1. Can an agent reliably answer operational questions ("Which causes cost the most delay minutes
>    on route X in period Y?") and rules questions ("How should a delay caused by a trespasser be
>    attributed?") and know which kind it's being asked?
> 2. For classifying terse incident descriptions into official reason codes, when does a
>    LoRA-fine-tuned 1–3B open model beat prompting a frontier API model on accuracy, cost and latency?

## Why this data is different

Nobody's portfolio has a rail copilot. The data is real, messy and domain-heavy:
- **Records:** hundreds of thousands of delay events per four-week period.
- **Free text:** terse, jargon-laden incident descriptions such as `"2O45 PASS COMM TOM"` and `"SEA MILLS OBSTRUCTION"`.
- **The rulebook:** a 218-page rulebook (DAPR, the Delay Attribution Principles and Rules) that humans actually use to settle these questions, plus about 50 published rulings on disputed cases.

## Data

| Source | What | Access | Licence |
|--------|------|--------|---------|
| Network Rail historic delay attribution | Monthly zips from 2018-19 P01 to 2023-24 P09. ~40 columns: `INCIDENT_REASON`, `INCIDENT_DESCRIPTION`, `RESPONSIBLE_MANAGER`, `TOC_CODE`, `PFPI_MINUTES`, stanox locations, event type. One period ≈ 580k rows, ~78k unique incidents, 212 reason codes | Public Azure blob container `historic-delay-attribution` (linked from Network Rail's data pages); glossary in `Reference Files/` | OGL |
| Delay Attribution Principles and Rules (DAPR), Sept 2026 edition | 218 pages, ~79k words, includes cause-code tables | Blob container `delay-attribution-board` | *Check*: likely OGL; confirm before vendoring |
| Delay Attribution Board guidance | ~26 process guides (PGD01–26), ~52 rulings on disputed cases (DAB001–053) | Same container | As above |

## Scope

**Must have**
- **Ingestion:** DuckDB loading of 2–3 years of periods. Deduplicate on `INCIDENT_NUMBER` + create date, and handle cancellation "deemed minutes" separately.
- **Retrieval:**
  - Hybrid BM25 + embedding search over DAPR, PGDs and rulings, with reranking.
  - Chunk by section, with citations back to the section number.
- **Text-to-SQL tool:** a schema description, read-only access, row limits, and query validation before execution.
- **The agent:**
  - It routes between the two tools and can use both (e.g. "how many incidents last period were attributed under reason X, and what does DAPR say X covers?").
  - It refuses questions outside its scope.
- **An MCP server** exposing `search_rules`, `query_delays` and `classify_incident`.
- **Evaluation suite:**
  - A golden set of ~150 questions (SQL, rules, mixed, unanswerable).
  - Scoring: execution accuracy for SQL, citation-grounded answer scoring for RAG, and an LLM-as-judge calibrated against my own labels.
  - It runs in CI and fails the build if accuracy regresses.
- **Cost and latency tracking** per query, with a small dashboard.
- **Failure-mode analysis:** a written taxonomy of what goes wrong, with examples.

**Fine-tune vs prompt experiment**
- **Task:** `INCIDENT_DESCRIPTION` (plus event type and location) → `INCIDENT_REASON`. Restrict to the top ~30 codes plus "other".
- **Compared:**
  - (a) a TF-IDF + logistic regression baseline
  - (b) a LoRA/QLoRA fine-tune of a ~1–3B model with Hugging Face `peft`
  - (c) a frontier API model, few-shot, with the code table from DAPR in context
- **Report:** macro-F1, cost per 1k requests, p50/p95 latency, and the crossover point where each option wins.

**Stretch:** a Streamlit or Gradio demo on a Hugging Face Space; guardrails for prompt injection via retrieved text.

**Out of scope:** live train-running feeds, and predicting future delays.

## Design decisions to write up

- When the agent should use SQL, retrieval or both, and how routing errors show up in the evals.
- Chunking a legal-style rulebook, including cross-references between sections.
- Judge calibration: agreement between my labels and the LLM judge.
- Why the baseline matters: if TF-IDF gets 90%, say so.

## Risks and gotchas

- **Data freshness:** published delay data stops at Dec 2023. Frame the project as historical analysis. DAPR is current, so rules may have changed since the data period; note this in answers.
- **Blob URLs aren't a stable API.** Mirror a small OGL-licensed sample in the repo so CI and demos never depend on them.
- **Class imbalance** across 212 codes, which is why the task is restricted to the top-N codes.
- **API keys** must never be committed. CI evals use a small, cached subset to control cost.

## Done when

- [ ] `make eval` prints accuracy / cost / latency tables, and CI runs it
- [ ] MCP server works from Claude Desktop or Claude Code, with a short demo GIF (animated screen capture) in the README
- [ ] Fine-tune vs prompt results table with a written recommendation
- [ ] Failure-mode write-up
