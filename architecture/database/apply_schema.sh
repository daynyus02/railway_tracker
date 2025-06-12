# Connects to the database locally and runs schema.sql file.
source .env
export PGPASSWORD = $DB_PASSWORD
psql -h $DB_HOST -U $DB_USER $DB_NAME -c "schema.sql"