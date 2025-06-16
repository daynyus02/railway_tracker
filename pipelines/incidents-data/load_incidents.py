"""A script to load data from the National Rail Incidents API to the RDS."""

from os import environ as ENV
import logging

from dotenv import load_dotenv
import pandas as pd
from psycopg2 import connect
from psycopg2.extras import execute_values
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
            logger.error("Missing operator ID for %s.", operator_name)
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
            logger.error("Missing station ID for %s.", station_name)
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

    with conn.cursor() as cur:
        q = """
            SELECT route_id FROM route
            WHERE origin_station_id = %s AND destination_station_id = %s AND operator_id = %s
            ;
            """
        cur.execute(q, (origin_station_id, destination_station_id, operator_id))

        route = cur.fetchone()
        if not route:
            logger.error("Missing route ID for %s to %s operated by %s.",
                         origin, destination, operator)
            raise ValueError("Could not find matching route.")

    logging.info("Found route ID: %s", route[0])
    return route[0]


def get_existing_incident_keys(conn) -> set[tuple[str, str]]:
    """Fetch all existing (incident_number, version_number) keys from the incident table."""
    with conn.cursor() as cur:
        cur.execute("SELECT incident_number, version_number FROM incident")
        return set(cur.fetchall())


def insert_incidents(conn, data, route_id: int):
    """Insert incident data if it's not already in the database."""
    existing_keys = get_existing_incident_keys(conn)

    new_records = []
    for _, row in data.iterrows():
        key = (row["incident_number"], row["version_number"])
        if key in existing_keys:
            logger.debug("Skipping duplicate incident %s", key)
            continue

        new_records.append((
            route_id,
            row["start_time"],
            row["end_time"],
            row["description"],
            row["incident_number"],
            row["version_number"],
            row["is_planned"],
            row["info_link"],
            row["summary"]
        ))

    if not new_records:
        logger.info("No new incidents to insert.")
        return

    with conn.cursor() as cur:
        execute_values(
            cur,
            """
            INSERT INTO incident (
                route_id, start_time, end_time, description,
                incident_number, version_number, is_planned,
                info_link, summary
            )
            VALUES %s
            """,
            new_records
        )
    conn.commit()
    logger.info("Inserted %s new incident records.", len(new_records))


if __name__ == "__main__":
    load_dotenv()
    connection = get_connection()
    get_route_id(connection, "London Paddington",
                 "Bristol Temple Meads", "Great Western Railway")
    connection.close()
