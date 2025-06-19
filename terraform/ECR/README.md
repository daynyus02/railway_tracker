# `/terraform/ECR`

All terraform files to provision ECR repositories are here.

## Set up

Create a `terraform.tfvars` file locally, and populate it with:

- ACCESS_KEY - AWS IAM access key.
- SECRET_KEY - The corresponding secret key for the above IAM user.

## Resources provisioned

#### ECR Repository:
- `c17-trains-ecr-rtt-pipeline`
- Hosts the image for the RTT pipeline lambda to run.

#### ECR Repository:
- `c17-trains-ecr-incidents-pipeline`
- Hosts the image for the Incidents pipeline lambda to run.

#### ECR Repository:
- `c17-trains-ecr-reports`
- Hosts the image for the Reports lambda to run.

#### ECR Repository:
- `c17-trains-ecr-dashboard`
- Hosts the image for the dashboard task definition to run.

## Provisioning Resources

To provision resources run the following commands:

`terraform plan`  
`terraform apply`