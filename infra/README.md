# Infrastructure

Terraform for the portfolio's live services. Each is a container image on AWS Lambda behind a
function URL (IAM-signed by default, optionally public), in `eu-west-2`.

| Folder | What |
|---|---|
| `bootstrap/` | One-off per account: the remote-state bucket, cost budget and GitHub OIDC provider |
| `modules/lambda_container_service/` | ECR repo, Lambda function, function URL, logs, and the GitHub deploy role |
| `projects/p1/` | P1's service, calling the module |

Sign in with `aws login` (no access keys), then apply `bootstrap/` first; see its README.

## Adding a project

Copy `projects/p1/main.tf`, change the state `key`, `name` and sizing. The module needs no changes.

## First apply

Lambda can't be created without an image, so the first apply is in three steps. After that, the
deploy workflow (T31) pushes images and updates the function; Terraform ignores which image is live.

```bash
cd infra/projects/p1
terraform init -backend-config="bucket=tfstate-<account-id>-eu-west-2"

# 1. The ECR repository only
terraform apply -target=module.service.aws_ecr_repository.this

# 2. Push one image tagged `bootstrap` (arm64), from the repo root
REPO=$(terraform -chdir=infra/projects/p1 output -raw ecr_repository_url)
aws ecr get-login-password | docker login --username AWS --password-stdin "${REPO%%/*}"
# --provenance=false: Lambda rejects the multi-manifest index that build attestations produce
docker buildx build --platform linux/arm64 --provenance=false --push \
  -f projects/01-fulfilment-optimisation/Dockerfile -t "$REPO:bootstrap" .

# 3. Everything else
terraform apply
```

## Calling a private URL

Function URLs are private by default (`public = false`): only requests signed by an identity in the
account get through. For a demo, sign with your `aws login` session, which expires on its own:

```bash
eval "$(aws configure export-credentials --format env)"
URL=$(terraform -chdir=infra/projects/p1 output -raw function_url)
curl --aws-sigv4 "aws:amz:eu-west-2:lambda" \
  --user "$AWS_ACCESS_KEY_ID:$AWS_SECRET_ACCESS_KEY" \
  -H "x-amz-security-token: $AWS_SESSION_TOKEN" \
  -H "content-type: application/json" \
  -d @projects/01-fulfilment-optimisation/examples/batch_request.json \
  "${URL}batch"
```

Setting `public = true` opens the URL to anyone; reserved concurrency then caps what abuse can cost.

`terraform destroy` removes the service, including its images. The state bucket in `bootstrap/` is
protected from destroy.
