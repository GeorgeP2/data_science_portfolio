# T15: Retrospective analysis: total left on the table

**Phase:** 4 Analysis · **Estimate:** 3 h · **Depends on:** T09, T11

## Ask

Compare lifters' actual jumps with the optimised plan under the fitted model. How much expected total
is left on the table, and where (by attempt and by lift)?

## Why

Answers headline question 2 and produces the "total left on the table" chart that "Done when" requires.

## How

- For each test-set lifter-meet: expected total of the actual choices vs the optimal policy, both under
  the model.
- Aggregate by lift and attempt number, with bootstrap intervals over meets.
- The optimised policy was never deployed and its outcomes are never observed, so present results as
  model-based estimates. State the selection bias: jump size is confounded with how the lifter feels
  on the day.
- Aggregate results only: no per-lifter rankings or profiles.

## Plan

- [ ] Expected total of actual choices
- [ ] Gap vs the optimal policy per lifter-meet
- [ ] Aggregation with intervals
- [ ] Chart by attempt and by lift
- [ ] Limitations paragraph

## Acceptance criteria

- [ ] Chart by attempt and by lift saved to `reports/figures/`
- [ ] Every figure shows uncertainty intervals
- [ ] Limitations (model-based, selection bias, noisy identities) stated next to the chart
- [ ] No output identifies an individual lifter
