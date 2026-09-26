# T21 (stretch): Live plan updating

**Phase:** Stretch · **Estimate:** 2 h · **Depends on:** T16

## Ask

After each attempt, update the lifter's meet-day max by Bayesian updating on the outcome and
re-optimise the rest of the plan.

## Why

Makes the demo usable during a meet, and uses the latent-strength model directly.

## How

- Posterior over the meet-day max conditioned on the makes and misses so far (grid or particle
  approximation for speed).
- Demo: enter each outcome and see the updated next attempt.

## Plan

- [ ] Only start once T01–T19 are done
- [ ] Updating function
- [ ] Re-optimisation with the updated distribution
- [ ] Demo UI for entering outcomes

## Acceptance criteria

- [ ] A make raises and a miss lowers the estimated max (test)
- [ ] Updated plans still pass the T12 property tests
- [ ] Update and re-plan complete in under 1 s
