# T16: Scheduled daily run

**Phase:** 4 Platform · **Estimate:** 1.5 h · **Depends on:** T15

## Ask

Schedule the flow to run daily on fresh NESO data, and let it build up MLflow history.

## Why

"Done when" requires a scheduled daily run with visible MLflow history. Cloud deployment (Terraform)
is stretch, so this must work without it.

## How

- A Prefect deployment with a daily cron schedule, run by a local worker or Prefect Cloud's free tier.
  Decide which and note the trade-off (a local worker only runs while the machine is on).
- Let it run for at least a week, then capture the MLflow run history for the README.

## Plan

- [ ] Choose where the scheduler runs
- [ ] Create the deployment with a cron schedule
- [ ] Confirm the first scheduled run succeeds
- [ ] Collect a week of runs

## Acceptance criteria

- [ ] At least 7 consecutive daily runs are visible in MLflow
- [ ] Failed runs, if any, show a readable reason in Prefect
- [ ] How to start the schedule is documented in the README
