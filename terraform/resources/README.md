# `/terraform/resources`

Terraform files to provision resources for the project are here.

## Set up

Create a `terraform.tfvars` file locally, and populate it with:

- ACCESS_KEY - AWS IAM access key.
- SECRET_KEY - The corresponding secret key for the above IAM user.
- ACCOUNT_ID - AWS Account ID.
- VPC_ID - The ID of the VPC to use.
- SUBNET_ID_X - The ID's of subnets to use.
- DB_HOST - RDS instance endpoint.
- DB_NAME - Database name.
- DB_USER - Database username.
- DB_PASSWORD - Database password.
- DB_PORT - Database port.
- API_USERNAME - RTT API username.
- API_PASSWORD - RTT API password.
- STATIONS - Comma separated list of stations to be loaded.
- GW_URL - URL for the incidents API (Great Western Railway services only).

## Resources provisioned

#### Lambda:
- `c17-trains-lambda-rtt-pipeline`
- Runs the RTT ETL pipeline.

#### Lambda:
- `c17-trains-lambda-incidents-pipeline`
- Runs the incidents ETL pipeline.

#### Scheduler:
- `c17-trains-schedule-rtt-pipeline`
- Schedules the RTT ETL pipeline lambda to run every 5 minutes.

#### Scheduler:
- `c17-trains-schedule-incidents-pipeline`
- Schedules the incidents ETL pipeline lambda to run every 1 hour.

## Provisioning Resources

To provision resources run the following commands:

`terraform plan`  
`terraform apply`