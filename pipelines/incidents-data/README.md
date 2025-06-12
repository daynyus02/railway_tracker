## `pipelines/incident-data`

## Overview
The directory contains the ETL pipeline for the National Rail Incidents API.

This pipeline extracts train service data from the National Rail Incidents API and processes it into a structured DataFrame format. The data is then transformed before being uploaded to an RDS database hosted on AWS RDS.

## Explanation
`extract.py` - Extract data from the API and turn it into a pandas dataframe.

## Setup and Installation
1. Create and activate a new virtual environment 
- `python3 -m venv .venv`
- `source .venv/bin/activate`
2. Install all dependencies.
- `pip install -r requirements.txt`
3. Ensure that environment variables are stored locally in a `.env` file.

### Example `.env`
```bash
GW_URL = XXX
```

## Usage
Run `python3 extract.py` in the command line.