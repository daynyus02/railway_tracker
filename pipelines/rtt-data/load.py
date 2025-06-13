"""Script for loading data into RDS."""

import logging
from os import environ as ENV

import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
from psycopg2 import connect, OperationalError
from psycopg2.extensions import connection as Connection
from psycopg2.extras import RealDictCursor

from extract import fetch_train_data
from transform import transform_train_data

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def get_connection() -> Connection:
    """Return a database connection."""
    logger.info("Establishing connection to database...")
    try:
        conn = connect(
            dbname=ENV["DB_NAME"],
            user=ENV["DB_USER"],
            password=ENV["DB_PASSWORD"],
            host=ENV["DB_HOST"],
            port=ENV["DB_PORT"],
            cursor_factory=RealDictCursor
        )
        logger.info("Successfully connected to database.")
        return conn
    except OperationalError as e:
        logger.error("Failed to connect to database: %s", e)
        raise


def load_data_from_database(conn: Connection) -> DataFrame:
    """Loading all the data from the database."""
    query = """
        SELECT
            ts.service_uid,
            ts.train_identity,
            s.station_name,
            s.station_crs,
            o_station.station_name AS origin_name,
            d_station.station_name AS destination_name,
            tstop.scheduled_arr_time,
            tstop.actual_arr_time,
            tstop.scheduled_dep_time,
            tstop.actual_dep_time,
            op.operator_name,
            ts.service_date,
            tstop.platform,
            tstop.platform_changed,
            CASE WHEN c.cancellation_id IS NOT NULL THEN TRUE ELSE FALSE END AS cancelled,
            c.reason AS cancel_reason
        FROM train_service ts
        JOIN route r ON ts.route_id = r.route_id
        JOIN station o_station ON r.origin_station_id = o_station.station_id
        JOIN station d_station ON r.destination_station_id = d_station.station_id
        JOIN train_stop tstop ON ts.train_service_id = tstop.train_service_id
        JOIN station s ON tstop.station_id = s.station_id
        JOIN operator op ON r.operator_id = op.operator_id
        LEFT JOIN cancellation c ON tstop.train_stop_id = c.train_stop_id;
    """

    with conn.cursor() as curs:
        logger.info("Executing query...")
        curs.execute(query)
        rows = curs.fetchall()
        logger.debug("Fetched %d rows from database.", len(rows))
        train_df = DataFrame(rows)
        logger.debug("DataFrame created.")
    logger.info("Successfully fetched data from database.")
    return train_df


def load_data_into_database(data: DataFrame, conn: Connection) -> None:
    """Load data into the database. """
    print(data)


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as db_connection:
        logger.info("Connection established.")
        # stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
        # result = fetch_train_data(stations)
        # transformed_data = transform_train_data(result)
        # load_data_into_database(transformed_data, db_connection)
        load_data_from_database(db_connection)
