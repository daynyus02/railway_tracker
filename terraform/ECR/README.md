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

## Provisioning Resources

To provision resources run the following commands:

`terraform plan`  
`terraform apply`