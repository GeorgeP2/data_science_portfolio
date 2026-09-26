# T25: Deploy to Cloud Run

**Phase:** 6 Service · **Estimate:** 1.5 h · **Depends on:** T24

## Ask

Deploy the container to Cloud Run with a public endpoint.

## Why

"Done when" requires a live endpoint. A live demo is cheap here and makes the project checkable.

## How

- Artifact Registry + `gcloud run deploy`; scripted in a `make deploy` target or shell script.
- Min instances 0 to stay free-tier; note cold-start effect on latency.
- Cap max instances and request size to limit cost exposure.

## Plan

- [ ] GCP project, registry and service account
- [ ] Deploy script
- [ ] Deploy and smoke-test with the example `curl`

## Acceptance criteria

- [ ] Public URL returns a valid batching result for the example request
- [ ] Deployment is reproducible from the script
- [ ] Max instances and request limits are set
