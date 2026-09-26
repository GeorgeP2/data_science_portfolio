# T11: Agent: routing, combining tools and refusing

**Phase:** 3 Agent · **Estimate:** 3 h · **Depends on:** T09, T10

## Ask

Build the agent that chooses `query_delays`, `search_rules`, both, or a refusal.

## Why

Headline question 1: can the agent answer both kinds of question and know which kind it's being asked?

## How

- Tool-use loop on the Claude API (model ID from config) with T09 and T10 as tools.
- System prompt defines scope (historical GB rail delay attribution) and refusal behaviour.
- Log each step (tool calls, tokens, latency) for T13 and the evals.

## Plan

- [ ] Tool definitions
- [ ] Agent loop with a step limit
- [ ] Scope and refusal prompt
- [ ] Trace logging
- [ ] Manual check on ~10 questions across SQL, rules, mixed and unanswerable

## Acceptance criteria

- [ ] Answers a mixed question by calling both tools (count under reason X + what DAPR says X covers)
- [ ] Refuses out-of-scope questions (e.g. live running, predicting future delays)
- [ ] Every run produces a trace with tool calls, tokens and latency
- [ ] The step limit stops runaway loops
