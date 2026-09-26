# T26 (stretch): Hugging Face Space demo

**Phase:** Stretch · **Estimate:** 3 h · **Depends on:** T11, T25

## Ask

Deploy a Streamlit or Gradio demo of the copilot to a Hugging Face Space.

## Why

A live demo lets readers try the agent without cloning the repo.

## How

- Uses the committed OGL data sample only; rulebook index built at startup from fetched documents
  (or vendored only if T03 confirmed OGL).
- API key as a Space secret; rate-limit and cap spend per session.

## Plan

- [ ] Only start once T01–T25 are done
- [ ] Minimal chat UI showing tool calls and citations
- [ ] Deploy with secret and limits
- [ ] Link from README

## Acceptance criteria

- [ ] Public Space answers a SQL, a rules and a mixed example question
- [ ] No key in the repo or Space files; spend cap documented
- [ ] Linked from the README
