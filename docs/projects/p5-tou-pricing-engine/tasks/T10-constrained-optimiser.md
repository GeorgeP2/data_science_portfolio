# T10: Constrained tariff schedule optimiser

**Phase:** 3 Optimiser · **Estimate:** 3 h · **Depends on:** T09

## Ask

Given costs and elasticities, find the 48-half-hour price schedule that maximises margin, subject to a
margin floor, an Ofgem-style price cap and a maximum step change between consecutive half-hours.

## Why

This is the "known optimum" in headline question 1. It is the oracle the bandit is scored against and
the engine behind the Streamlit app.

## How

- Discretise prices to a grid, which makes the non-linear demand response tractable. Then solve as a
  MIP or with CP-SAT (the brief links this to Project 1's CP-SAT work). Record which and why.
- Constraints, all in `config.yaml`: a price cap per half-hour, a margin floor (define whether it's an
  average or a daily total), and a limit on |p[t] − p[t−1]|.
- Return the schedule, the margin and the binding constraints. Report infeasibility explicitly.

## Plan

- [ ] Write down the formulation and grid resolution
- [ ] Implement
- [ ] Compare against brute force on a tiny instance (few periods, coarse grid)
- [ ] Handle infeasible inputs

## Acceptance criteria

- [ ] Matches brute force on small instances
- [ ] Solves a 48-period day in under 1 s on the default grid
- [ ] Returns a clear infeasible status when constraints conflict
- [ ] Formulation documented in the module docstring
