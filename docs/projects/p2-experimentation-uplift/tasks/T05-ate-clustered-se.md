# T05: ATE per arm with household-clustered standard errors

**Phase:** 1 Field experiment basics · **Estimate:** 2 h · **Depends on:** T03

## Ask

Estimate the average treatment effect of each mailing on turnout, with standard errors clustered on
household, and compare them with naive individual-level SEs.

## Why

Randomisation was by household, so individuals aren't independent. Showing how much naive SEs
understate uncertainty is the core of the "clustered vs individual randomisation" write-up.

## How

- OLS `voted ~ C(treatment)` with cluster-robust SEs on `hh_id` (statsmodels).
- Cross-check with a household-level bootstrap; report the SE ratio (design effect) per arm.
- Compare point estimates with the published GGL results (confirm the published values first).

## Plan

- [ ] Naive and clustered regressions
- [ ] Household bootstrap cross-check
- [ ] Design-effect table
- [ ] Forest plot of ATEs with both CIs

## Acceptance criteria

- [ ] Point estimates match the paper to its reported precision, or differences are explained
- [ ] Clustered and bootstrap SEs agree within 10%
- [ ] Table shows naive SE, clustered SE and their ratio per arm
- [ ] Forest plot saved to `reports/figures/`
