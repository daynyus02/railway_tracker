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

# ECR Repository and image for RTT pipeline lambda

data "aws_ecr_repository" "rtt_pipeline_lambda_image-repo" {
  name = "c17-trains-ecr-rtt-pipeline"
}

data "aws_ecr_image" "rtt_pipeline_lambda_image_version" {
  repository_name = data.aws_ecr_repository.rtt_pipeline_lambda_image-repo.name
  image_tag       = "latest"
}

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

# RTT Pipeline Lambda Security Group

resource "aws_security_group" "rtt_pipeline_lambda_sg" {
  name        = "c17-trains-sg-rtt-pipeline-lambda"
  description = "Allow Lambda to access the internet and RDS."
  vpc_id      = data.aws_vpc.c17_vpc.id
}

resource "aws_vpc_security_group_egress_rule" "rtt_pipeline_lambda_egress" {
  security_group_id = aws_security_group.rtt_pipeline_lambda_sg.id
  cidr_ipv4         = "0.0.0.0/0"
  from_port         = 0
  to_port           = 0
  ip_protocol       = "-1"
  description       = "Allow all outbound traffic"
}

# RTT Pipeline Lambda

resource "aws_lambda_function" "rtt_pipeline_lambda" {
  function_name = "c17-trains-lambda-rtt-pipeline"
  description   = "Runs the RTT ETL Pipeline every five minutes. Triggered by an EventBridge."
  role          = aws_iam_role.pipeline_lambda_role.arn
  package_type  = "Image"
  image_uri     = data.aws_ecr_image.rtt_pipeline_lambda_image_version.image_uri
  timeout       = 900

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

  vpc_config {
    security_group_ids = [aws_security_group.rtt_pipeline_lambda_sg.id]
    subnet_ids         = [data.aws_subnet.public_subnet_1.id, data.aws_subnet.public_subnet_2.id, data.aws_subnet.public_subnet_3.id]
  }
}