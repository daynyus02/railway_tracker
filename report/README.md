## Report

### Overview
This directory contains the scripts for an AWS Lambda which creates PDF summary reports of a train station's performance (delays, cancellations) from the previous day's data in the RDS database.

### Explanation
`extract.py` - Extracts data from the RDS for each station from the previous day.   
`test_extract.py` - Tests for the extract script.   
`transform_summary.py` - Transforms data into summary statistics for PDF report.  
`test_transform_summary.py` - Tests for the transform script.  
`report.py` - Generates report using summary statistics.  
`load.py` - Loads reports into S3 bucket.  
`conftest.py` - Contains fixtures for the tests.     

### Setup and Installation
1. Create and activate a new virtual environment.
- `python3 -m venv .venv`
- `source .venv/bin/activate`
2. Install all dependencies.
- `pip install -r requirements.txt`
3. Ensure the following environment variables are stored locally in a `.env` file:
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_NAME`
- `DB_PORT`=5432
- `S3_BUCKET_NAME`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`

### Usage
1.
2.
3.

