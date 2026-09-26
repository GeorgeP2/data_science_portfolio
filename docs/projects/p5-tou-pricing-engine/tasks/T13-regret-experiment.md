# T13: Regret experiment and curve

**Phase:** 4 Bandit · **Estimate:** 1.5 h · **Depends on:** T10, T12

## Ask

Run the bandit, the oracle and a static tariff over many simulated days and seeds, and plot
cumulative regret.

## Why

The regret curve is the first "done when" item and the README's headline chart.

## How

- Oracle: T10 run each day with the true elasticities. Static tariff: a flat rate and/or an LCL-style
  fixed ToU, chosen and stated before the run.
- Cumulative regret against the oracle for the bandit and the static tariff, averaged over seeds with
  an uncertainty band.
- Save the figure with `portfolio.plotting.save_fig` to `reports/figures/` and the metrics via
  `portfolio.evaluation`.

## Plan

- [ ] Experiment runner with seeds and horizon in `config.yaml`
- [ ] Regret computation
- [ ] Plot

## Acceptance criteria

- [ ] One command regenerates the figure and metrics
- [ ] Bandit regret grows sub-linearly over the horizon, with static regret shown for contrast
- [ ] Figure shows the mean and an uncertainty band across ≥ 20 seeds
