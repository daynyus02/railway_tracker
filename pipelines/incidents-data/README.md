## `pipelines/incident-data`

## Overview
The directory contains the ETL pipeline for the National Rail Incidents API.

This pipeline extracts train service data from the National Rail Incidents API and processes it into a structured DataFrame format. The data is then transformed before being uploaded to an RDS database hosted on AWS RDS.

It also sends alerts for new and updated incidents on defined routes.

## Explanation
- `extract_incidents.py` - Extracts data from the API and turns it into a pandas DataFrame.
- `test_extract_incidents.py` - Tests for the extract script.
- `transform_incidents.py` - Transforms and filters extracted data.
- `test_transform_incidents.py` - Tests for the transform script.
- `load_incidents.py` - Loads new incidents into the database, updates updated incidents in the database, and skips incidents already present.
- `test_load_incidents.py` - Tests for the load script.
- `conftest.py` - Contains fixtures for the tests.
- `alerts_incidents.py` - Contains functions to publish alerts for new/updated incidents.
- `deploy_image.bash` - Commands to build and deploy the image to AWS.


## Setup and Installation
1. Install AWS CLI.
- [Installation instructions here.](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. Install Docker Desktop.
- [Installation instructions here.](https://docs.docker.com/desktop/)
3. Ensure that environment variables are stored locally in a .env file.

### Example `.env`
```
ECR_IMAGE_URI - ECR image URI
IMAGE_NAME - Local image tag name
AWS_ECR_REGISTRY - ECR registry URL
```

## Usage
Build and upload an image to the ECR using `bash deploy_image.bash`.