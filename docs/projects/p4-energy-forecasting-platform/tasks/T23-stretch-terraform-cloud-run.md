# T23 (stretch): Terraform for Cloud Run and a scheduled job

**Phase:** Stretch · **Estimate:** 3 h · **Depends on:** T16, T20

## Ask

Define the Cloud Run service (API + dashboard) and a scheduled Cloud Run job for the daily flow in
Terraform.

## Why

Moves the daily run off a local machine and makes the infrastructure reproducible.

## How

- Terraform for Artifact Registry, Cloud Run service(s), a Cloud Run job, and Cloud Scheduler.
- MLflow backend and artefacts need persistent storage (e.g. a GCS bucket); decide and document.
- Min instances 0 and capped max instances to stay near free tier.

## Plan

- [ ] Only start once T01–T22 are done
- [ ] Terraform modules
- [ ] Move MLflow storage to persistent storage
- [ ] `terraform apply` and verify the scheduled job

## Acceptance criteria

- [ ] `terraform apply` from a clean state creates everything; `terraform destroy` removes it
- [ ] The scheduled job runs daily and logs to MLflow
- [ ] Public dashboard URL is in the README
