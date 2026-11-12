variable "aws_region" {
  type        = string
  description = "AWS region"
  default     = "eu-central-1"
}

variable "vpc_id" {
  type        = string
  description = "Existing VPC ID. Uses the default VPC when unset."
  default     = null
}

variable "app_secret_arn" {
  type        = string
  description = "ARN of the Secrets Manager JSON with APP_PASSWORD, JWT_SECRET and GRAFANA_ADMIN_PASSWORD."
}

variable "release_bucket" {
  type        = string
  description = "Existing S3 bucket for release archives under releases/."
}
