"""A script to load data from the National Rail Incidents API to the RDS."""

from os import environ as ENV
import logging

from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect, Connection

from extract_incidents import extract
from transform_incidents import transform

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def get_connection() -> Connection:
    """Get a connection to the RDS."""
    return connect(
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"]
    )


def get_operator_ids(conn: Connection, operator_name: str) -> int:
    """Get operator id's from their name."""

    with conn.cursor() as cur:
        logger.debug("Getting operator ID for %s.", operator_name)
        cur.execute(
            "SELECT operator_id FROM operator WHERE operator_name = %s;", (operator_name,))

        operator = cur.fetchone()
        if not operator:
            raise ValueError(f"Could not find operator ID for {operator_name}")

    return operator
