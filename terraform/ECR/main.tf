provider "aws" {
  region     = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY
}

# ECR Repository for RTT pipeline image

resource "aws_ecr_repository" "rtt_pipeline_lambda_image_repo" {
  name = "c17-trains-ecr-rtt-pipeline"
}

# ECR Repository for Incidents pipeline image

resource "aws_ecr_repository" "incidents_pipeline_lambda_image_repo" {
  name = "c17-trains-ecr-incidents-pipeline"
}

# ECR Repository for reports lambda image

resource "aws_ecr_repository" "reports_lambda_image_repo" {
  name = "c17-trains-ecr-reports"
}

# ECR Repository for dashboard image

resource "aws_ecr_repository" "dashboard_td_image_repo" {
  name = "c17-trains-ecr-dashboard"
}