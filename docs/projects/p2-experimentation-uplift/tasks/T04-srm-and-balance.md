# T04: Sample-ratio mismatch and covariate balance

**Phase:** 1 Field experiment basics · **Estimate:** 1.5 h · **Depends on:** T03

## Ask

Check randomisation: SRM on arm sizes and covariate balance across arms.

## Why

Nothing downstream is trustworthy if randomisation failed. It's the first check in any A/B analysis.

## How

- SRM: chi-squared test of arm counts against the intended allocation, at **household** level (the
  unit of randomisation) as well as individual level. Confirm the intended allocation from the paper.
- Balance: standardised mean differences (SMD) for each pre-treatment covariate per arm vs control,
  plus a joint test (regress treatment on covariates with clustered SEs).

## Plan

- [ ] SRM at household and individual level
- [ ] SMD table and a love plot
- [ ] Joint balance test
- [ ] Unit tests on synthetic data with a known imbalance

## Acceptance criteria

- [ ] SRM p-values reported at both levels, with the intended allocation cited
- [ ] SMD table covers every pre-treatment covariate; any |SMD| > 0.1 is called out
- [ ] Tests detect an injected imbalance and pass a balanced synthetic set
- [ ] Love plot saved to `reports/figures/`
