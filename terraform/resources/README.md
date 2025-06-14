# `/terraform/resources`

Terraform files to provision resources for the project are here.

## Set up

Create a `terraform.tfvars` file locally, and populate it with:

- ACCESS_KEY - AWS IAM access key.
- SECRET_KEY - The corresponding secret key for the above IAM user.
- ACCOUNT_ID - AWS Account ID.
- EMAIL - An email to subscribe to SNS topic.
- VPC_ID - The ID of the VPC to use.
- SUBNET_ID_X - The ID's of subnets to use.
- DB_HOST - RDS instance endpoint.
- DB_NAME - Database name.
- DB_USER - Database username.
- DB_PASSWORD - Database password.
- DB_PORT - Database port.
- API_USERNAME - RTT API username.
- API_PASSWORD - RTT API password.

## Resources provisioned

#### SNS Topic:
- `c17-trains-sns-topic-rtt-pipeline-alerts`
- For RTT pipeline alerts.

#### Lambda:
- `c17-trains-lambda-rtt-pipeline`
- Runs the RTT ETL pipeline.

#### Scheduler:
- `c17-trains-schedule-rtt-pipeline`
- Schedules the RTT ETL pipeline lambda to run every 5 minutes.

## Provisioning Resources

To provision resources run the following commands:

`terraform plan`  
`terraform apply`