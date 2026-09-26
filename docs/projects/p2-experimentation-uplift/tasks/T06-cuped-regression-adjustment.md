# T06: CUPED and regression adjustment

**Phase:** 1 Field experiment basics · **Estimate:** 2 h · **Depends on:** T05

## Ask

Use prior participation (`g2000`, `p2000`, `g2002`, `p2002`, `p2004`) to reduce variance, and report
the effective sample-size gain.

## Why

GGL's pre-treatment history is exactly what CUPED needs. The gain translates directly into smaller
or shorter experiments, which feeds the power calculator and the speed question.

## How

- CUPED with a combined pre-period covariate, and full regression adjustment (treatment × centred
  covariates, Lin 2013 style), both with clustered SEs.
- Effective sample-size gain = (SE_unadjusted / SE_adjusted)².
- A deliberate trap example: adjusting for a post-treatment variable to show the bias. Construct it
  synthetically if GGL has no post-treatment column.

## Plan

- [ ] Reusable CUPED function
- [ ] Regression adjustment
- [ ] Compare covariate sets
- [ ] Post-treatment-variable trap demo
- [ ] Tests: CUPED on synthetic data recovers the true effect with lower variance

## Acceptance criteria

- [ ] Adjusted ATEs fall within the unadjusted CIs
- [ ] Variance reduction and effective sample-size gain reported per arm
- [ ] Covariate-set comparison table shows which covariates earn their place
- [ ] Trap demo shows a biased estimate with a one-line explanation
