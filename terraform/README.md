# `/terraform`

## Overview
Contains all the files for terraform configurations.

## Explanation
- `/ECR` - Contains all ECR repositories for the project.
- `/resources` - Contains resources needed for the project.

## Setup and Installation

To install terraform, please follow the guidance on their [official website](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli).

## Usage
1. Move into a directory.
- `cd ECR`
2. Initialise Terraform.
- `terraform init`
3. Apply configuration.
- `terraform apply`

Note: Apply the configuration in `/ECR` first as the other resources rely on using images stored in the ECR repositories.