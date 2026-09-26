# T20: Dockerfile and one-command local run

**Phase:** 4 Platform · **Estimate:** 1 h · **Depends on:** T18, T19

## Ask

Containerise the API and dashboard so the platform runs locally with one command.

## Why

Every project ships with a Dockerfile and a one-command local run (`docs/projects/README.md`). It's
also the prerequisite for the Terraform stretch task.

## How

- One image with two entrypoints (API, dashboard), or a small `docker compose` file with both services
  plus MLflow.
- Mount or bake in a small model artefact so it runs without the full data.

## Plan

- [ ] Dockerfile
- [ ] Compose file (if used)
- [ ] README "Run locally" section

## Acceptance criteria

- [ ] One documented command starts the API and dashboard
- [ ] `curl` on `/forecast` returns a forecast from inside the container
- [ ] Image contains no raw LCL or NESO data
