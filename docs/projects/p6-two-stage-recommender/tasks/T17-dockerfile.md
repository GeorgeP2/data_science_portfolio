# T17: Dockerfile and one-command local run

**Phase:** 5 Serving · **Estimate:** 1 h · **Depends on:** T15

## Ask

Containerise the serving API with its artefacts so it runs locally with one command.

## Why

Every project ships with a Dockerfile and a one-command local run (`docs/projects/README.md`).

## How

- Slim Python base, non-root user. Artefacts (cache, features, ranker) mounted or built in a
  documented step; no raw data in the image.
- A small demo artefact set built from a user sample, so the container starts without the full dataset.

## Plan

- [ ] Demo artefact build step
- [ ] Dockerfile
- [ ] README "Run locally" section

## Acceptance criteria

- [ ] `docker run` + one `curl` returns recommendations
- [ ] Image contains no raw data
- [ ] Image size stated in the README
