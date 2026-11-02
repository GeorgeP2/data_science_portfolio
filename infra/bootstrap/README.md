# Bootstrap: Terraform state bucket

Creates the S3 bucket that stores remote state for every other config in `infra/`: versioned,
encrypted, private and TLS-only. Other configs lock state with S3 native locking
(`use_lockfile = true`), so there's no DynamoDB table.

It also creates a monthly AWS Budget (default $10, `budget_limit_usd`) that emails at 50% and 100% of
actual spend and at 100% of forecast spend. Set the alert address in `terraform.tfvars`
(git-ignored):

```hcl
budget_alert_email = "you@example.com"
```

Run once per account, signed in with `aws login`:

```bash
cd infra/bootstrap
terraform init
terraform apply
```

The bucket is named `tfstate-<account-id>-<region>` (the `state_bucket` output). Other configs pass
it to their S3 backend at init time, so the account ID isn't committed:

```bash
terraform init -backend-config="bucket=tfstate-<account-id>-eu-west-2"
```

This config's own state stays local in `terraform.tfstate` (git-ignored). If it's lost, the bucket
is still there; bring it back under management with
`terraform import aws_s3_bucket.state <bucket>` and the matching imports for the other resources.
The bucket has `prevent_destroy` set, so `terraform destroy` here fails on purpose.
