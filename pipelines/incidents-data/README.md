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
- `alerts_incidents.py` - Contains functions to publish alerts for new/updated incidents.
- `test_alerts_incidents.py` - Tests for the alerts script.
- `conftest.py` - Contains fixtures for the tests.



## Setup and Installation
1. Create and activate a new virtual environment.
- `python3 -m venv .venv`
- `source .venv/bin/activate`
2. Install all dependencies.
- `pip install -r requirements.txt`
3. Ensure that environment variables are stored locally in a `.env` file.

### Example `.env`
```
INCIDENTS_URL = XXX - URL for incidents API.
DB_HOST = XXX
DB_NAME = XXX
DB_USER = XXX
DB_PASSWORD = XXX
DB_PORT = XXX
```

## Usage
Build a docker file with `docker build -t [tag_name] .`
Run the image with `docker run --env-file .env [tag_name]`