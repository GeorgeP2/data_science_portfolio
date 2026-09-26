# T14: IPS, SNIPS and doubly-robust estimators

**Phase:** 5 OPE · **Estimate:** 2 h · **Depends on:** T01

## Ask

Implement IPS, self-normalised IPS and doubly-robust off-policy value estimators, with confidence
intervals.

## Why

Headline question 2 depends on them. Writing them myself, rather than only calling a library, shows
the bias/variance trade-offs the write-up discusses.

## How

- Inputs: logged contexts, actions, rewards, logging propensities and the target policy's action
  probabilities. DR also takes a simple regression reward model, fitted with cross-fitting.
- Bootstrap confidence intervals.
- Cross-check against the `obp` library's implementations on the same inputs.

## Plan

- [ ] IPS and SNIPS
- [ ] DR with a cross-fitted reward model
- [ ] Bootstrap CIs
- [ ] Tests on synthetic logs where the true value is known

## Acceptance criteria

- [ ] On synthetic logs, each estimator's 95% CI covers the true value in ≥ 90% of repeats
- [ ] Point estimates match `obp` within numerical tolerance
- [ ] Degenerate cases (zero propensity, unsupported actions) raise clear errors
