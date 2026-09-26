# T12: CP-SAT batching model

**Phase:** 3 Solvers · **Estimate:** 3 h · **Depends on:** T10, T11

## Ask

Formulate order batching in OR-Tools CP-SAT and solve it under a time limit.

## Why

Shows exact-method modelling and gives near-optimal reference solutions on small instances. It also
drives the "why CP-SAT and not MIP" write-up.

## How

- Routing distance isn't linear in batch membership, so pick one: a set-partitioning model over
  pre-generated candidate batches (costed by the router), or an aisle-based distance approximation.
  Record the choice and its effect on optimality.
- Warm-start with the savings solution (T11). Register a solution callback so the incumbent is
  available for the anytime contract.
- Time limit and worker count from `config.yaml`.

## Plan

- [ ] Choose and write down the formulation
- [ ] Implement model build + solve
- [ ] Solution hint from savings
- [ ] Incumbent callback
- [ ] Tests on tiny instances against brute-force enumeration

## Acceptance criteria

- [ ] Matches brute force on instances small enough to enumerate
- [ ] Never worse than its warm start
- [ ] Respects the deadline to within 50 ms and returns the incumbent when it stops early
- [ ] Formulation and its approximation (if any) are documented
