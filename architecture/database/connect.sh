# Connects to the database if .env is correctly set up.
source .env
export PGPASSWORD=$DB_PASSWORD
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT