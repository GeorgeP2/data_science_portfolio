# T17: Evidently drift reports and the 2013 ToU replay

**Phase:** 4 Platform · **Estimate:** 2.5 h · **Depends on:** T04, T05, T07

## Ask

Add Evidently drift reports to the platform, and on LCL replay time through 2013 to show the ToU
trial triggering drift alerts.

## Why

"Done when" requires a drift report showing the 2013 ToU trial detected. It's a real distribution
shift, so it tests whether the monitoring works rather than being staged.

## How

- Reference window: pre-trial data. Replay month by month (or week by week) through 2013, comparing
  each window to the reference.
- Monitor both input features (e.g. consumption by time of day) and forecast residuals.
- Confirm the trial dates and which households were in the ToU group before interpreting results.
  Compare ToU households against the Std group as a control: drift should show in ToU but not in Std.
- Also add a drift report step for the national flow (T15), on recent vs training data.

## Plan

- [ ] Confirm trial dates and group membership
- [ ] Reference and replay windows
- [ ] Evidently reports per window, ToU vs Std
- [ ] Alert rule and a timeline chart of drift scores
- [ ] Drift step in the national flow

## Acceptance criteria

- [ ] Drift alerts fire for ToU households during the trial period
- [ ] Std households show no (or much weaker) drift over the same windows
- [ ] HTML report and timeline chart are saved; the timeline is in `reports/figures/`
- [ ] The national flow produces a drift report each run
