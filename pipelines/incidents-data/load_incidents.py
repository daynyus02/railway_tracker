"""A script to load data from the National Rail Incidents API to the RDS."""

from os import environ as ENV
import logging

from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extensions import connection as Connection

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


def get_operator_id(conn: Connection, operator_name: str) -> int:
    """Get the operator id for an operator."""
    with conn.cursor() as cur:
        logger.debug("Getting operator ID for %s.", operator_name)
        cur.execute(
            "SELECT operator_id FROM operator WHERE operator_name = %s;", (operator_name,))

        operator_id = cur.fetchone()
        if not operator_id:
            logger.warning("Missing operator ID for %s.", operator_name)
            raise ValueError(f"Could not find operator ID for {operator_name}")

    return operator_id[0]


def get_station_id(conn: Connection, station_name: str) -> int:
    """Get the station id for a station."""
    with conn.cursor() as cur:
        logger.debug("Getting station ID for %s.", station_name)
        cur.execute(
            "SELECT station_id FROM station WHERE station_name = %s;", (station_name,))

        station_id = cur.fetchone()
        if not station_id:
            logger.warning("Missing station ID for %s.", station_name)
            raise ValueError(f"Could not find station ID for {station_name}.")

    return station_id[0]


def get_route_id(conn: Connection, origin: str, destination: str, operator: str) -> int:
    """Get the route id for an origin, destination and operator."""
    logger.debug("Getting route id for: %s to %s, operated by %s.",
                 origin, destination, operator)

    origin_station_id = get_station_id(conn, origin)
    destination_station_id = get_station_id(conn, destination)
    operator_id = get_operator_id(conn, operator)
    logger.info("Fetched ids: origin: %s, destination: %s, operator: %s",
                origin_station_id, destination_station_id, operator_id)


if __name__ == "__main__":
    load_dotenv()
    connection = get_connection()
    get_route_id(connection, "London Paddington",
                 "Bristol Temple Meads", "Great Western Railway")
    connection.close()
