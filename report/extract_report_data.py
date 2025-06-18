"""Script for extracting last 24 hours of data for summary reports."""

from os import environ as ENV
import logging

from psycopg2 import connect, OperationalError
from psycopg2.extras import RealDictCursor
from psycopg2.extensions import connection as Connection
from dotenv import load_dotenv
from pandas import DataFrame

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="WARNING",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def get_db_connection() -> Connection:
    """Gets a connection to the trains database."""

    try:
        conn = connect(
            user=ENV["DB_USER"],
            password=ENV["DB_PASSWORD"],
            host=ENV["DB_HOST"],
            port=ENV["DB_PORT"],
            database=ENV["DB_NAME"]
        )
        logging.info("Successfully retrieved database connection.")
    except OperationalError:
        logging.error("Failed to get database connection.")
        raise

    return conn


def get_station_id_from_crs(station_crs: str, conn: Connection) -> int:
    """Gets corresponding station ID from database for a given station CRS code."""

    with conn.cursor(cursor_factory=RealDictCursor) as curs:

        curs.execute("SELECT * FROM station WHERE station_crs = %s",
                     (station_crs,))
        result = curs.fetchone()

        if result:
            logging.info(
                "Successfully retrieved station ID for %s", station_crs)
            result = dict(result)["station_id"]
        else:
            logging.warning("No station ID retrieved for %s", station_crs)
        curs.close()

    return result


def get_days_data_per_station(station_crs: str, conn: Connection) -> list[dict]:
    """Get data from the last 24 hours for a given station."""

    station_id = get_station_id_from_crs(station_crs, conn)

    query = """
            SELECT * FROM train_stop
            JOIN station AS s
            USING (station_id)
            JOIN train_service
            USING (train_service_id)
            LEFT JOIN cancellation
            USING (train_stop_id)
            WHERE s.station_id = %s
            AND service_date = current_date - 1;
            """

    with conn.cursor(cursor_factory=RealDictCursor) as curs:

        curs.execute(query, (station_id,))
        result = curs.fetchall()

        if result:
            logging.info(
                "Successfully retrieved past day's data for %s", station_crs)
            result = [dict(row) for row in result]
        else:
            logging.warning("No past data retrieved for %s", station_crs)
        curs.close()

    return result


if __name__ == "__main__":
    load_dotenv()

    db_conn = get_db_connection()

    stations = ["PAD", "RDG", "DID", "SWI", "CPM", "BTH", "BRI"]

    for station in stations:
        get_days_data_per_station(station, db_conn)
