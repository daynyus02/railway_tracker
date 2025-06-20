## Report

### Overview
This directory contains the scripts for an AWS Lambda which creates PDF summary reports of a train station's performance (delays, cancellations) from the previous day's data in the RDS database. The Lambda sends emails to subscribed users with relevant summary reports attached using AWS SES.

### Explanation
`extract_reports.py` - Extracts data from the RDS for each station from the previous day.   
`test_extract_reports.py` - Tests for the extract script.   
`transform_summary.py` - Transforms data into summary statistics for PDF report.  
`test_transform_summary.py` - Tests for the transform script.  
`report.py` - Generates report using summary statistics.
`test_report.py` - Tests for the report generation script.
`load_reports.py` - Loads reports into S3 bucket.
`test_load_reports.py` - Tests for the load script.
`main_reports.py` - The ETL pipeline to create reports and email them to subscribers to relevant SNS topics.
`Dockerfile` - File to create a container image for the reports pipeline.  
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
- `ACCESS_KEY`
- `SECRET_ACCESS_KEY`
- `SENDER_EMAIL`

### Usage
Build a docker file with docker build -t [tag_name] . Run the image with docker run --env-file .env [tag_name]

