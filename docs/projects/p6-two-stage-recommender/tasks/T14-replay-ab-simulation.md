# T14: Replay-based simulated A/B

**Phase:** 4 Analysis · **Estimate:** 2.5 h · **Depends on:** T11

## Ask

Compare two policies with a replay-based offline A/B and report the difference with a confidence
interval.

## Why

The brief asks for a simulated A/B. It turns metric differences into a treatment effect with
uncertainty, which is how the result would be judged in practice.

## How

- Policies: best retriever alone vs the two-stage pipeline (confirm this is the intended pair).
- Replay estimator: step through test events in time order; a policy is credited only when its
  recommendation matches the logged event. Report match rates.
- CI by bootstrapping over users.
- Caveat: the logging policy isn't uniformly random, so replay is biased towards policies that
  resemble the production recommender; report organic-only replay alongside.

## Plan

- [ ] Replay loop
- [ ] Bootstrap CI
- [ ] Organic-only variant
- [ ] Short results note

## Acceptance criteria

- [ ] Reports each policy's replay reward, the difference and a 95% CI
- [ ] Match counts per policy are reported so sample size is visible
- [ ] The logging-policy bias caveat is stated in the results note
- [ ] Deterministic for a fixed seed
