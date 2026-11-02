variable "name" {
  description = "Name for the function, ECR repository, log group and roles."
  type        = string
}

variable "image_tag" {
  description = "Tag of the image the function is created with. Later deploys are CI's job (T31); Terraform ignores the image after creation."
  type        = string
}

variable "architecture" {
  type    = string
  default = "arm64"
}

variable "memory_mb" {
  description = "CPU scales with memory; 1769 MB is one full vCPU."
  type        = number
  default     = 1769
}

variable "timeout_s" {
  type    = number
  default = 30
}

variable "public" {
  description = "Open the function URL to anyone. Off: only IAM-signed requests from the account get through."
  type        = bool
  default     = false
}

variable "reserved_concurrency" {
  description = "Cap on concurrent instances, so a public URL can't run up the bill. null: no reservation, only the account limit. AWS keeps 10 unreserved, so this needs an account limit above 10."
  type        = number
  default     = null
}

variable "environment" {
  type    = map(string)
  default = {}
}

variable "readiness_check_path" {
  description = "Path the Lambda Web Adapter polls until the app is up."
  type        = string
  default     = "/health"
}

variable "log_retention_days" {
  type    = number
  default = 14
}

variable "ecr_keep_images" {
  type    = number
  default = 10
}

variable "github_repo" {
  description = "owner/name of the repo whose main branch may deploy, via the account's GitHub OIDC provider."
  type        = string
}

variable "github_branch" {
  type    = string
  default = "main"
}
