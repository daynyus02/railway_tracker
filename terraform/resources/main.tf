provider "aws" {
  region     = var.REGION
  access_key = var.ACCESS_KEY
  secret_key = var.SECRET_KEY
}

# VPC and subnets

data "aws_vpc" "c17_vpc" {
  id = var.VPC_ID
}

data "aws_subnet" "public_subnet_1" {
  id = var.SUBNET_ID_1
}

data "aws_subnet" "public_subnet_2" {
  id = var.SUBNET_ID_2
}

data "aws_subnet" "public_subnet_3" {
  id = var.SUBNET_ID_3
}

# ECR

# ECR Repository and image for RTT pipeline lambda

data "aws_ecr_repository" "rtt_pipeline_lambda_image-repo" {
  name = "c17-trains-ecr-rtt-pipeline"
}

data "aws_ecr_image" "rtt_pipeline_lambda_image_version" {
  repository_name = data.aws_ecr_repository.rtt_pipeline_lambda_image-repo.name
  image_tag       = "latest"
}

# SNS

# SNS topic for RTT pipeline alerts

resource "aws_sns_topic" "rtt_pipeline_alerts_topic" {
  name = "c17-trains-sns-topic-rtt-pipeline-alerts"
}

resource "aws_sns_topic_subscription" "rtt_pipeline_alerts_sub" {
  topic_arn = aws_sns_topic.rtt_pipeline_alerts_topic.arn
  protocol  = "email"
  endpoint  = var.EMAIL
}

# LAMBDA

# Permissions for RTT pipeline lambda

data "aws_iam_policy_document" "pipeline_lambda_role_trust_policy_doc" {
  statement {
    effect = "Allow"
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
    actions = [
      "sts:AssumeRole"
    ]
  }
}

data "aws_iam_policy_document" "pipeline_lambda_role_permissions_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:eu-west-2:${var.ACCOUNT_ID}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "sns:Publish"
    ]
    resources = [aws_sns_topic.rtt_pipeline_alerts_topic.arn]
  }
}

resource "aws_iam_role" "pipeline_lambda_role" {
  name               = "c17-trains-pipeline-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.pipeline_lambda_role_trust_policy_doc.json
}

resource "aws_iam_policy" "pipeline_lambda_role_permissions_policy" {
  name   = "c17-trains-pipeline-lambda-permissions-policy"
  policy = data.aws_iam_policy_document.pipeline_lambda_role_permissions_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "pipeline_lambda_role_policy_connection" {
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = aws_iam_policy.pipeline_lambda_role_permissions_policy.arn
}

# RTT Pipeline Lambda

resource "aws_lambda_function" "rtt_pipeline_lambda" {
  function_name = "c17-trains-lambda-rtt-pipeline"
  description   = "Runs the RTT ETL Pipeline every five minutes. Triggered by an EventBridge."
  role          = aws_iam_role.pipeline_lambda_role.arn
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.rtt_pipeline_lambda_image_version.image_uri
  timeout       = 240
  memory_size   = 128
  depends_on    = [aws_iam_role_policy_attachment.pipeline_lambda_role_policy_connection]

  environment {
    variables = {
      DB_HOST      = var.DB_HOST
      DB_NAME      = var.DB_NAME
      DB_USER      = var.DB_USER
      DB_PASSWORD  = var.DB_PASSWORD
      DB_PORT      = var.DB_PORT
      API_USERNAME = var.API_USERNAME
      API_PASSWORD = var.API_PASSWORD
    }
  }
}

# EVENTBRIDGE

# Scheduler permissions

resource "aws_iam_role" "scheduler_role" {
  name = "EventBridgeSchedulerRole-c17-trains"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "eventbridge_invoke_lambda_policy" {
  name = "EventBridgeInvokePolicy-c17-trains"
  role = aws_iam_role.scheduler_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "lambda:InvokeFunction"
        Effect = "Allow"
        Resource = [
          aws_lambda_function.rtt_pipeline_lambda.arn
        ]
      }
    ]
  })
}

# Scheduler for RTT pipeline lambda

resource "aws_scheduler_schedule" "rtt_pipeline_lambda_schedule" {
  name       = "c17-trains-schedule-rtt-pipeline"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(*/5 * * * ? *)"

  target {
    arn      = aws_lambda_function.rtt_pipeline_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}