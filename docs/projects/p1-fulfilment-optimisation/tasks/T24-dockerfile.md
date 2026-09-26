# T24: Dockerfile and one-command local run

**Phase:** 6 Service · **Estimate:** 1 h · **Depends on:** T22

## Ask

Containerise the service so `docker run` + one `curl` reproduces a batching result.

## Why

This is the first "done when" item, and the prerequisite for Cloud Run.

## How

- Slim Python base, multi-stage build, non-root user, `PORT` env var (Cloud Run convention).
- Ship an example request JSON (generated, not a benchmark instance) in the repo.

## Plan

- [ ] Dockerfile
- [ ] Example request file
- [ ] README "Run locally" section with the exact commands

## Acceptance criteria

- [ ] `docker build` + `docker run` + the documented `curl` returns batches and routes
- [ ] Image contains no raw benchmark data
- [ ] Image size stated in the README
