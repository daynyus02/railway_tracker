## Database

## Overview
The database containing train data is a PostgreSQL database hosted on AWS RDS. This directory contains files to connect to the database locally and populate the database with the relevant data tables.

## Explanation
- `schema.sql` resets the database. All tables are dropped if they exist and then re-created to populate the database according to the project ERD.
- `connect.sh` is a shell script which connects you to the database locally using the correct credentials.
- `apply_schema.sh` is a shell script which connects you to the database locally and runs the schema file to populate the database.

## Setup and Installation
1. Create a `.env` file with the following credentials:
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_NAME`
- `DB_PORT` = 5432


## Usage
1. Run the `apply_schema.sh` shell script to populate the database.
- `bash apply_schema.sh`