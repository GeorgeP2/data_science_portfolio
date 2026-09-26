# T12: Power calculator

**Phase:** 2 Heterogeneous effects · **Estimate:** 2.5 h · **Depends on:** T05, T06

## Ask

Build a small power calculator (CLI, optionally Streamlit) that uses the variance estimates from the
data, including the clustering design effect and the CUPED variance reduction.

## Why

"Done when" requires a power calculator usable by someone else. Grounding it in real variance
estimates is what separates it from a textbook formula.

## How

- Core function: required sample size (or MDE) given baseline rate, MDE (or n), alpha, power, ICC /
  household size, and CUPED variance-reduction factor.
- Defaults pre-filled from T05/T06 estimates.
- CLI via `argparse`; a thin Streamlit front end only if time allows (core logic stays in `src/`).
- Validate against `statsmodels` power functions for the unclustered, unadjusted case.

## Plan

- [ ] Core sample-size / MDE function
- [ ] Design-effect and CUPED adjustments
- [ ] CLI with `--help`
- [ ] Optional Streamlit page
- [ ] Tests against statsmodels and a hand-computed clustered case

## Acceptance criteria

- [ ] Matches statsmodels to within 1% in the simple case
- [ ] Clustered and CUPED-adjusted results match a hand calculation
- [ ] Someone else can run it from the README instructions alone
- [ ] Defaults cite where they came from (T05/T06 outputs)
