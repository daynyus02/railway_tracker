## Report

### Overview
This directory contains the scripts for an AWS Lambda which creates PDF summary reports of a train station's performance (delays, cancellations) from the previous day's data in the RDS database.

### Explanation
`extract_report_data.py` - Extracts data from the RDS for each station from the previous day.   
`test_extract_incidents.py` - Tests for the extract script.   
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

### Usage
1.
2.
3.

