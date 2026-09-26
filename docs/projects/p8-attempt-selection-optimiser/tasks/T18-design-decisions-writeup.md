# T18: Design decisions write-up

**Phase:** 6 Write-up · **Estimate:** 2 h · **Depends on:** T07, T09, T14, T15

## Ask

Write the "Design decisions & trade-offs" section covering the four decisions in the brief.

## Why

Every project ships with this section; it's where judgement is visible.

## How

1. Latent strength vs direct classifier: use the T07 and T09 probability-vs-jump curves.
2. Evaluating a policy that was never deployed: what can and can't be claimed (links to off-policy
   evaluation in Project 5).
3. Choice of objective: how the three objectives change risk behaviour (T13 and T14 examples).
4. Pooling structure: which groupings matter, with evidence (e.g. group-level posterior spread, or a
   comparison with a less pooled fit).

## Plan

- [ ] Draft the four subsections
- [ ] Link each claim to a figure, table or test

## Acceptance criteria

- [ ] All four decisions covered, each with the alternative considered
- [ ] Every quantitative claim points to a reproducible result
