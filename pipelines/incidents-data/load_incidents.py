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


def get_operator_id_map(conn: Connection) -> dict[str, int]:
    """Return a dict mapping operator names to operator IDs."""
    logger.debug("Fetching operator ID map.")
    with conn.cursor() as cur:
        cur.execute("SELECT operator_name, operator_id FROM operator")
        return {row[0]: row[1] for row in cur.fetchall()}


def get_station_id_map(conn: Connection) -> dict[str, int]:
    """Return a dict mapping station names to station IDs."""
    logger.debug("Fetching station ID map.")
    with conn.cursor() as cur:
        cur.execute("SELECT station_name, station_id FROM station")
        return {row[0]: row[1] for row in cur.fetchall()}


def get_route_id(conn: Connection, origin: str, destination: str, operator: str,
                 station_id_map: dict[str, int], operator_id_map: dict[str, int]) -> int:
    """Get the route id for an origin, destination and operator."""
    logger.debug("Getting route id for: %s to %s, operated by %s.",
                 origin, destination, operator)
    try:
        origin_station_id = station_id_map[origin]
        destination_station_id = station_id_map[destination]
        operator_id = operator_id_map[operator]
    except KeyError as e:
        logger.error("Missing ID for route lookup: %s", e)
        raise ValueError(f"Could not find ID for route lookup: {e}")

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


def get_existing_incident_keys(conn: Connection) -> dict[str, str]:
    """Return a dict of incident_number: version_number from the DB."""
    with conn.cursor() as cur:
        cur.execute("SELECT incident_number, version_number FROM incident")
        return {row[0]: row[1] for row in cur.fetchall()}


def insert_incidents(conn: Connection, data: pd.DataFrame):
    """Insert incident data if it's not already in the database."""
    existing_versions = get_existing_incident_keys(conn)
    operator_id_map = get_operator_id_map(conn)
    station_id_map = get_station_id_map(conn)

    route_cache = {}

    inserted_count = 0
    updated_count = 0
    skipped_count = 0

    for _, row in data.iterrows():
        logger.debug("Started handling an extracted incident.")
        incident_number = row["incident_number"]
        version_number = row["version_number"]
        key = (incident_number, version_number)

        operator_names = [op.strip() for op in row["operators"].split(";")]
        operator_ids = []

        for name in operator_names:
            operator_id = operator_id_map.get(name)
            if operator_id:
                operator_ids.append(operator_id)
            else:
                logger.warning(
                    "Operator %s not found in database. Skipping.", name)

        if not operator_ids:
            logger.warning(
                "No valid operators for incident %s. Skipping.", key)
            continue

        route_key = ("London Paddington",
                     "Bristol Temple Meads", operator_names[0])

        if route_key in route_cache:
            route_id = route_cache[route_key]
            logger.info("Found cached route ID: %s.", route_id)
        else:
            try:
                route_id = get_route_id(conn, "London Paddington", "Bristol Temple Meads",
                                        operator_names[0], station_id_map, operator_id_map)
                route_cache[route_key] = route_id
            except ValueError:
                logger.warning(
                    "No valid route found for incident %s. Skipping.", key)
                continue

        with conn.cursor() as cur:
            if incident_number not in existing_versions:
                logger.debug("Inserting new incident.")

                insert_query = """
                INSERT INTO incident (
                    route_id, start_time, end_time, description,
                    incident_number, version_number, is_planned,
                    info_link, summary
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING incident_id
                ;
                """

                values = (route_id,
                          row["start_time"],
                          row["end_time"],
                          row["description"],
                          row["incident_number"],
                          row["version_number"],
                          row["is_planned"],
                          row["info_link"],
                          row["summary"])

                # cur.execute(insert_query, values)
                inserted_count += 1
                logger.info("Inserted new incident %s.", incident_number)

            elif existing_versions[incident_number] != version_number:
                logger.debug("Updating existing incident.")
                update_query = """
                    UPDATE incident
                    SET route_id = %s,
                        start_time = %s,
                        end_time = %s,
                        description = %s,
                        version_number = %s,
                        is_planned = %s,
                        info_link = %s,
                        summary = %s
                    WHERE incident_number = %s
                    RETURNING incident_id;
                """

                values = (
                    route_id,
                    row["start_time"],
                    row["end_time"],
                    row["description"],
                    version_number,
                    row["is_planned"],
                    row["info_link"],
                    row["summary"],
                    incident_number
                )

                # cur.execute(update_query, values)
                updated_count += 1
                logger.info("Updated incident %s to version %s.",
                            incident_number, version_number)

            else:
                skipped_count += 1
                logger.info("Skipping unchanged incident %s.", incident_number)
                continue

            # incident_id = cur.fetchone()[0]
            # assignment_values = [(incident_id, op_id)
            #                      for op_id in operator_ids]
            # assignment_query = """
            # INSERT INTO incident_operator_assignment
            #     (incident_id, operator_id)
            # VALUES %s
            # ON CONFLICT DO NOTHING;
            # """
            # execute_values(cur, assignment_query, assignment_values)

    conn.commit()
    logger.info("Inserted %s new incidents.", inserted_count)
    logger.info("Updated %s incidents.", updated_count)
    logger.info("Skipped %s duplicated incidents.", skipped_count)


def load(data: pd.DataFrame):
    """Main load process."""
    with get_connection() as conn:
        insert_incidents(conn, data)


if __name__ == "__main__":
    load_dotenv()
    data = extract()
    transformed = transform(data)
    load(transformed)
