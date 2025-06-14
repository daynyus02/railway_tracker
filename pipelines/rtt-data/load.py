"""Script for loading data into RDS."""

import logging
from os import environ as ENV

from pandas import DataFrame

from dotenv import load_dotenv
from psycopg2 import connect, DatabaseError
from psycopg2.extensions import connection as Connection
from psycopg2.extras import RealDictCursor
from psycopg2.extras import execute_batch

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
    except DatabaseError as e:
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

    with conn.cursor() as cur:
        logger.info("Executing query...")
        cur.execute(query)
        rows = cur.fetchall()
        logger.debug("Fetched %d rows from database.", len(rows))
        train_df = DataFrame(rows)
        logger.debug("DataFrame created.")
    logger.info("Successfully fetched data from database.")
    return train_df


def update_station(api_data: DataFrame, conn: Connection):
    """Updates database's station table."""
    api_data_stations = api_data[[
        "station_crs", "station_name"]].drop_duplicates()

    with conn.cursor() as cur:
        cur.execute("SELECT station_crs, station_name FROM station;")
        rows = cur.fetchall()
        database_data_stations = DataFrame(rows)

    new_stations = api_data_stations[~api_data_stations["station_crs"].isin(
        database_data_stations["station_crs"])]

    if not new_stations.empty:
        logger.info("Updating station table with %s new stations.",
                    len(new_stations))
        new_station_tuples = list(
            new_stations.itertuples(index=False, name=None))
        try:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO station (station_crs, station_name) VALUES (%s, %s);
                    """,
                    new_station_tuples
                )
            conn.commit()
            logger.info("Station table has been updated.")
        except DatabaseError as e:
            conn.rollback()
            logger.error("Database error: %s", e)
            raise

    else:
        logger.info("No new stations to add.")


def update_operator(api_data: DataFrame, conn: Connection):
    """Updates database's operator table."""
    api_data_operators = api_data[[
        "operator_name"]].drop_duplicates()

    with conn.cursor() as cur:
        cur.execute("SELECT operator_name FROM operator;")
        rows = cur.fetchall()
        database_data_operators = DataFrame(rows)

    new_operators = api_data_operators[~api_data_operators["operator_name"].isin(
        database_data_operators["operator_name"])]

    if not new_operators.empty:
        logger.info("Updating operator table with %s new operators.",
                    len(new_operators))
        new_operator_tuples = list(
            new_operators.itertuples(index=False, name=None))
        try:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO operator (operator_name) VALUES (%s);
                    """,
                    new_operator_tuples
                )
            conn.commit()
            logger.info("Operator table has been updated.")
        except DatabaseError as e:
            conn.rollback()
            logger.error("Database error: %s", e)
            raise

    else:
        logger.info("No new operators to add.")


def update_route(api_data: DataFrame, conn: Connection):
    """Updates database's route table."""
    api_data_route = api_data[[
        "origin_name", "destination_name", "operator_name"]].drop_duplicates()

    with conn.cursor() as cur:
        cur.execute(
            "SELECT origin_station_id, destination_station_id, operator_id FROM route;")
        rows = cur.fetchall()
        database_data_route = DataFrame(rows)

        cur.execute(
            "SELECT station_id, station_crs, station_name FROM station;")
        rows = cur.fetchall()
        database_data_stations = DataFrame(rows)

        cur.execute("SELECT operator_id, operator_name FROM operator;")
        rows = cur.fetchall()
        database_data_operators = DataFrame(rows)

    station_name_to_id = dict(
        zip(database_data_stations["station_name"], database_data_stations["station_id"]))
    operator_name_to_id = dict(zip(
        database_data_operators["operator_name"], database_data_operators["operator_id"]))

    api_data_route["origin_station_id"] = api_data_route["origin_name"].map(
        station_name_to_id)
    api_data_route["destination_station_id"] = api_data_route["destination_name"].map(
        station_name_to_id)
    api_data_route["operator_id"] = api_data_route["operator_name"].map(
        operator_name_to_id)

    api_data_route.dropna(
        subset=["origin_station_id", "destination_station_id", "operator_id"], inplace=True)

    api_data_route = api_data_route.drop(
        columns=["origin_name", "destination_name", "operator_name"])

    api_data_route["origin_station_id"] = api_data_route["origin_station_id"].astype(
        int)
    api_data_route["destination_station_id"] = api_data_route["destination_station_id"].astype(
        int)
    api_data_route["operator_id"] = api_data_route["operator_id"].astype(int)

    database_data_route = set(
        database_data_route.itertuples(index=False, name=None)
    )

    api_data_route = set(
        api_data_route.itertuples(index=False, name=None)
    )

    new_routes = api_data_route - database_data_route

    if new_routes:
        logger.info("Updating route table with %s new routes.",
                    len(new_routes))
        new_route_tuples = list(new_routes)
        try:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO route (origin_station_id,
                                       destination_station_id,
                                       operator_id) 
                    VALUES (%s, %s, %s);
                    """,
                    new_route_tuples
                )
            conn.commit()
            logger.info("Route table has been updated.")
        except DatabaseError as e:
            conn.rollback()
            logger.error("Database error: %s", e)
            raise

    else:
        logger.info("No new routes to add.")


def load_data_into_database(api_data: DataFrame,
                            conn: Connection) -> None:
    """Load data into the database. """
    update_station(api_data, conn)
    update_operator(api_data, conn)
    update_route(api_data, conn)


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as db_connection:
        logger.info("Connection established.")
        stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
        fetched_data = fetch_train_data(stations)
        transformed_fetched_data = transform_train_data(fetched_data)
        database_train_data = load_data_from_database(db_connection)
        load_data_into_database(transformed_fetched_data, db_connection)
