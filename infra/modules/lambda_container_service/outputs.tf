output "function_name" {
  value = aws_lambda_function.this.function_name
}

output "function_url" {
  value = aws_lambda_function_url.this.function_url
}

output "ecr_repository_url" {
  value = aws_ecr_repository.this.repository_url
}

output "deploy_role_arn" {
  value = aws_iam_role.deploy.arn
}
