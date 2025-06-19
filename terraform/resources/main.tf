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

# S3 BUCKET

resource "aws_s3_bucket" "s3_bucket" {
  bucket        = "c17-trains-bucket-reports"
  force_destroy = true
}

# ECR

# ECR Repository and image for RTT pipeline lambda

data "aws_ecr_repository" "rtt_pipeline_lambda_image_repo" {
  name = "c17-trains-ecr-rtt-pipeline"
}

data "aws_ecr_image" "rtt_pipeline_lambda_image_version" {
  repository_name = data.aws_ecr_repository.rtt_pipeline_lambda_image_repo.name
  image_tag       = "latest"
}

# ECR Repository and image for incidents pipeline lambda

data "aws_ecr_repository" "incidents_pipeline_lambda_image_repo" {
  name = "c17-trains-ecr-incidents-pipeline"
}

data "aws_ecr_image" "incidents_pipeline_lambda_image_version" {
  repository_name = data.aws_ecr_repository.incidents_pipeline_lambda_image_repo.name
  image_tag       = "latest"
}

# ECR Repository and image for reports lambda

data "aws_ecr_repository" "reports_lambda_image_repo" {
  name = "c17-trains-ecr-reports"
}

data "aws_ecr_image" "reports_lambda_image_version" {
  repository_name = data.aws_ecr_repository.reports_lambda_image_repo.name
  image_tag       = "latest"
}

# ECR Repository and image for dashboard task definition

data "aws_ecr_repository" "dashboard_td_image_repo" {
  name = "c17-trains-ecr-dashboard"
}

data "aws_ecr_image" "dashboard_td_image_version" {
  repository_name = data.aws_ecr_repository.dashboard_td_image_repo.name
  image_tag       = "latest"
}

# ECS

# Cluster

data "aws_ecs_cluster" "c17_ecs_cluster" {
  cluster_name = "c17-ecs-cluster"
}

# Security Group

resource "aws_security_group" "ecs_sg" {
  name        = "c17-trains-ecs-sg"
  description = "Allow HTTP access to dashboard."
  vpc_id      = data.aws_vpc.c17_vpc.id
}

resource "aws_vpc_security_group_egress_rule" "allow_all" {
  security_group_id = aws_security_group.ecs_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Allow all outward access."
}

resource "aws_vpc_security_group_ingress_rule" "allow_http" {
  security_group_id = aws_security_group.ecs_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 8501
  to_port           = 8501
  ip_protocol       = "tcp"
  description       = "Allow HTTP access from anywhere."
}

# Permissions

data "aws_iam_policy" "cloudwatch_full_access" {
  arn = "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess"
}

data "aws_iam_policy" "ecs_full_access" {
  arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
}

data "aws_iam_policy" "ecr_full_access" {
  arn = "arn:aws:iam::aws:policy/AmazonElasticContainerRegistryPublicFullAccess"
}

data "aws_iam_policy" "ecs_service" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

data "aws_iam_policy" "s3_full_access" {
  arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

data "aws_iam_policy" "sns_full_access" {
  arn = "arn:aws:iam::aws:policy/AmazonSNSFullAccess"
}

resource "aws_iam_role" "ecs_task_exec_role" {
  name = "c17-trains-ecs-task-exec-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_cloudwatch" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = data.aws_iam_policy.cloudwatch_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_ecs" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = data.aws_iam_policy.ecs_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_ecr" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = data.aws_iam_policy.ecr_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_s3" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = data.aws_iam_policy.s3_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_sns" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = data.aws_iam_policy.sns_full_access.arn
}

resource "aws_iam_role_policy_attachment" "ecs_task_exec_ecs_role" {
  role       = aws_iam_role.ecs_task_exec_role.name
  policy_arn = data.aws_iam_policy.ecs_service.arn
}

# Log group

resource "aws_cloudwatch_log_group" "dashboard_log_group" {
  name = "/ecs/c17-trains-dashboard"
}

# Task Definition

resource "aws_ecs_task_definition" "dashboard_td" {
  depends_on               = [aws_iam_role_policy_attachment.ecs_task_exec_ecs_role]
  family                   = "c17-trains-td-dashboard"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 256
  memory                   = 512
  task_role_arn            = aws_iam_role.ecs_task_exec_role.arn
  execution_role_arn       = aws_iam_role.ecs_task_exec_role.arn

  container_definitions = jsonencode([
    {
      name      = "dashboard"
      image     = data.aws_ecr_image.dashboard_td_image_version.image_uri
      cpu       = 256
      memory    = 512
      essential = true

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.dashboard_log_group.name
          awslogs-region        = var.REGION
          awslogs-stream-prefix = "ecs"
        }
      }

      environment = [
        {
          name  = "DB_HOST"
          value = var.DB_HOST
        },
        {
          name  = "DB_PORT"
          value = var.DB_PORT
        },
        {
          name  = "DB_NAME"
          value = var.DB_NAME
        },
        {
          name  = "DB_USER"
          value = var.DB_USER
        },
        {
          name  = "DB_PASSWORD"
          value = var.DB_PASSWORD
        },
        {
          name  = "TOPIC_PREFIX"
          value = var.TOPIC_PREFIX
        },
        {
          name  = "ACCESS_KEY"
          value = var.ACCESS_KEY
        },
        {
          name  = "SECRET_ACCESS_KEY"
          value = var.SECRET_KEY
        },
        {
          name  = "REGION"
          value = var.REGION
        }
      ]
    }
  ])
}

# ECS Service

resource "aws_ecs_service" "dashboard_service" {
  depends_on       = [aws_iam_role_policy_attachment.ecs_task_exec_ecs_role]
  name             = "c17-trains-ecs-service-dashboard"
  cluster          = data.aws_ecs_cluster.c17_ecs_cluster.id
  task_definition  = aws_ecs_task_definition.dashboard_td.arn
  desired_count    = 1
  launch_type      = "FARGATE"
  platform_version = "LATEST"
  force_delete     = true

  network_configuration {
    subnets          = [data.aws_subnet.public_subnet_1.id, data.aws_subnet.public_subnet_2.id, data.aws_subnet.public_subnet_3.id]
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }
}

# LAMBDA

# Permissions

data "aws_iam_policy_document" "lambda_role_trust_policy_doc" {
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
    resources = ["arn:aws:logs:${var.REGION}:${var.ACCOUNT_ID}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "sns:*"
    ]
    resources = ["arn:aws:sns:${var.REGION}:${var.ACCOUNT_ID}:*"]
  }
}

data "aws_iam_policy_document" "reports_lambda_role_permissions_policy_doc" {
  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["arn:aws:logs:${var.REGION}:${var.ACCOUNT_ID}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ses:*"
    ]
    resources = ["arn:aws:ses:${var.REGION}:${var.ACCOUNT_ID}:*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:PutObject"
    ]
    resources = ["arn:aws:s3:${var.REGION}:${var.ACCOUNT_ID}:${aws_s3_bucket.s3_bucket.bucket}/*"]
  }
}

resource "aws_iam_role" "pipeline_lambda_role" {
  name               = "c17-trains-pipeline-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy_doc.json
}

resource "aws_iam_policy" "pipeline_lambda_role_permissions_policy" {
  name   = "c17-trains-pipeline-lambda-permissions-policy"
  policy = data.aws_iam_policy_document.pipeline_lambda_role_permissions_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "pipeline_lambda_role_policy_connection" {
  role       = aws_iam_role.pipeline_lambda_role.name
  policy_arn = aws_iam_policy.pipeline_lambda_role_permissions_policy.arn
}

resource "aws_iam_role" "reports_lambda_role" {
  name               = "c17-trains-reports-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_role_trust_policy_doc.json
}

resource "aws_iam_policy" "reports_lambda_role_permissions_policy" {
  name   = "c17-trains-reports-lambda-permissions-policy"
  policy = data.aws_iam_policy_document.reports_lambda_role_permissions_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "reports_lambda_role_policy_connection" {
  role       = aws_iam_role.reports_lambda_role.name
  policy_arn = aws_iam_policy.reports_lambda_role_permissions_policy.arn
}

# RTT Pipeline Lambda

resource "aws_lambda_function" "rtt_pipeline_lambda" {
  function_name = "c17-trains-lambda-rtt-pipeline"
  description   = "Runs the RTT ETL Pipeline every five minutes. Triggered by an EventBridge."
  role          = aws_iam_role.pipeline_lambda_role.arn
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.rtt_pipeline_lambda_image_version.image_uri
  timeout       = 240
  memory_size   = 512
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
      STATIONS     = var.STATIONS
    }
  }
}

# Incidents Pipeline Lambda

resource "aws_lambda_function" "incidents_pipeline_lambda" {
  function_name = "c17-trains-lambda-incidents-pipeline"
  description   = "Runs the Incidents ETL Pipeline every one hour. Triggered by an EventBridge."
  role          = aws_iam_role.pipeline_lambda_role.arn
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.incidents_pipeline_lambda_image_version.image_uri
  timeout       = 240
  memory_size   = 512
  depends_on    = [aws_iam_role_policy_attachment.pipeline_lambda_role_policy_connection]

  environment {
    variables = {
      DB_HOST       = var.DB_HOST
      DB_NAME       = var.DB_NAME
      DB_USER       = var.DB_USER
      DB_PASSWORD   = var.DB_PASSWORD
      DB_PORT       = var.DB_PORT
      INCIDENTS_URL = var.INCIDENTS_URL
      REGION        = var.REGION
      ACCESS_KEY    = var.ACCESS_KEY
      SECRET_KEY    = var.SECRET_KEY
    }
  }
}

# Reports Lambda

resource "aws_lambda_function" "reports_lambda" {
  function_name = "c17-trains-lambda-reports"
  description   = "Generates daily summary reports. Triggered by an EventBridge."
  role          = aws_iam_role.reports_lambda_role.arn
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.reports_lambda_image_version.image_uri
  timeout       = 240
  memory_size   = 512
  depends_on    = [aws_iam_role_policy_attachment.reports_lambda_role_policy_connection]

  environment {
    variables = {
      DB_HOST           = var.DB_HOST
      DB_NAME           = var.DB_NAME
      DB_USER           = var.DB_USER
      DB_PASSWORD       = var.DB_PASSWORD
      DB_PORT           = var.DB_PORT
      ACCESS_KEY        = var.ACCESS_KEY
      SECRET_ACCESS_KEY = var.SECRET_KEY
      S3_BUCKET_NAME    = aws_s3_bucket.s3_bucket.bucket
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
          aws_lambda_function.rtt_pipeline_lambda.arn,
          aws_lambda_function.incidents_pipeline_lambda.arn,
          aws_lambda_function.reports_lambda.arn
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

  schedule_expression = "cron(* * * * ? *)"

  target {
    arn      = aws_lambda_function.rtt_pipeline_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}

# Scheduler for Incidents pipeline lambda

resource "aws_scheduler_schedule" "incidents_pipeline_lambda_schedule" {
  name       = "c17-trains-schedule-incidents-pipeline"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 * * * ? *)"

  target {
    arn      = aws_lambda_function.incidents_pipeline_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}

# Scheduler for reports lambda

resource "aws_scheduler_schedule" "reports_lambda_schedule" {
  name       = "c17-trains-schedule-reports"
  group_name = "default"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 9 * * ? *)"

  target {
    arn      = aws_lambda_function.reports_lambda.arn
    role_arn = aws_iam_role.scheduler_role.arn
  }
}