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
    pass


def load_data_into_database(data: DataFrame, conn: Connection) -> None:
    """Load data into the database. """
    print(data)


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as db_connection:
        logger.info("Connection established.")
        stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
        result = fetch_train_data(stations)
        transformed_data = transform_train_data(result)
        load_data_into_database(transformed_data, db_connection)
