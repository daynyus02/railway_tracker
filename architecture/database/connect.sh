# Connects to the database locally if .env is correctly set up.
source .env
psql -u $DB_USER -p$DB_PASSWORD -h $DB_HOST $DB_NAME -P $DB_PORT -D $DB_NAME