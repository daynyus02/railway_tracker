variable "REGION" {
  type    = string
  default = "eu-west-2"
}

variable "ACCESS_KEY" {
  type = string
}

variable "SECRET_KEY" {
  type = string
}

variable "VPC_ID" {
  type = string
}

variable "ACCOUNT_ID" {
  type = string
}

variable "SUBNET_ID_1" {
  type        = string
  description = "Public subnet."
}

variable "SUBNET_ID_2" {
  type        = string
  description = "Public subnet."
}

variable "SUBNET_ID_3" {
  type        = string
  description = "Public subnet."
}

variable "DB_HOST" {
  type = string
}

variable "DB_NAME" {
  type = string
}

variable "DB_USER" {
  type = string
}

variable "DB_PASSWORD" {
  type = string
}

variable "DB_PORT" {
  type = string
}

variable "API_USERNAME" {
  type = string
}

variable "API_PASSWORD" {
  type = string
}