# P1 fulfilment optimisation: the POST /batch service on Lambda. See ../../README.md for apply order.

terraform {
  required_version = ">= 1.10"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }

  # bucket comes from -backend-config at init, so the account ID isn't committed.
  backend "s3" {
    key          = "projects/p1/terraform.tfstate"
    region       = "eu-west-2"
    use_lockfile = true
  }
}

provider "aws" {
  region = "eu-west-2"

  default_tags {
    tags = { project = "p1-fulfilment-optimisation" }
  }
}

module "service" {
  source = "../../modules/lambda_container_service"

  name        = "fulfilment-optimisation"
  image_tag   = "bootstrap"
  github_repo = "GeorgeP2/data_science_portfolio"
  public      = false # IAM-signed requests only; see ../../README.md for calling it

  # New-account cap. ALNS and CP-SAT are CPU-bound and CPU scales with memory: move to 1769
  # (one vCPU) once the cap lifts, before measuring p95 in T26.
  memory_mb = 512
  timeout_s = 30 # api.max_budget_ms (10 s) + cold start + margin
  # No reserved concurrency: the URL is private and the account limit is 10, all of which AWS keeps
  # unreserved. Set one before making the URL public.
}

output "function_url" {
  value = module.service.function_url
}

output "ecr_repository_url" {
  value = module.service.ecr_repository_url
}

output "function_name" {
  value = module.service.function_name
}

output "deploy_role_arn" {
  value = module.service.deploy_role_arn
}
