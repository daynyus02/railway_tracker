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


def find_new_routes(api_data_route: DataFrame,
                    database_data_route: DataFrame,
                    database_data_stations: DataFrame,
                    database_data_operators: DataFrame):
    """Finds new routes to add to db."""
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

    return new_routes


def find_new_train_services(api_data_train_service,
                            database_data_train_service,
                            database_data_stations,
                            database_data_operators,
                            database_data_routes):
    """Finds new train services to add to db."""
    station_name_to_id = dict(
        zip(database_data_stations["station_name"], database_data_stations["station_id"]))
    operator_name_to_id = dict(zip(
        database_data_operators["operator_name"], database_data_operators["operator_id"]))

    api_data_train_service["origin_station_id"] = api_data_train_service["origin_name"].map(
        station_name_to_id)
    api_data_train_service["destination_station_id"] = api_data_train_service["destination_name"].map(
        station_name_to_id)
    api_data_train_service["operator_id"] = api_data_train_service["operator_name"].map(
        operator_name_to_id)

    api_data_train_service.dropna(
        subset=["origin_station_id", "destination_station_id", "operator_id"], inplace=True)

    api_data_train_service = api_data_train_service.merge(
        database_data_routes,
        on=["origin_station_id", "destination_station_id", "operator_id"],
        how="left"
    )

    api_data_train_service.drop(
        columns=["origin_name", "destination_name", "operator_name",
                 "origin_station_id", "destination_station_id", "operator_id"],
        inplace=True
    )

    existing_service_uids = set(database_data_train_service['service_uid'])

    new_train_service = api_data_train_service[
        ~api_data_train_service['service_uid'].isin(existing_service_uids)
    ]

    return new_train_service


def map_api_train_stop_data(api_data_train_stop: DataFrame,
                            database_data_train_services: DataFrame,
                            database_data_stations: DataFrame):
    """Mapping train_service_id and station_id to API train stop data."""
    service_uid_to_id = dict(zip(
        database_data_train_services["service_uid"], database_data_train_services["train_service_id"]))
    station_name_to_id = dict(
        zip(database_data_stations["station_name"], database_data_stations["station_id"]))

    api_data_train_stop["train_service_id"] = api_data_train_stop["service_uid"].map(
        service_uid_to_id)
    api_data_train_stop["station_id"] = api_data_train_stop["station_name"].map(
        station_name_to_id)

    api_data_train_stop.dropna(
        subset=["train_service_id", "station_id"], inplace=True)

    api_data_train_stop.drop(
        columns=["service_uid", "station_name"], inplace=True)

    api_data_train_stop["train_service_id"] = api_data_train_stop["train_service_id"].astype(
        int)
    api_data_train_stop["station_id"] = api_data_train_stop["station_id"].astype(
        int)

    api_data_train_stop = api_data_train_stop[[
        "train_service_id", "station_id",
        "scheduled_arr_time", "actual_arr_time",
        "scheduled_dep_time", "actual_dep_time",
        "platform", "platform_changed"
    ]]

    return api_data_train_stop


def find_new_cancellations(api_data_cancellation,
                           database_data_cancellation,
                           database_data_train_services,
                           database_data_train_stop):
    """Finds new cancellations to add to db."""
    service_uid_to_id = dict(zip(
        database_data_train_services["service_uid"], database_data_train_services["train_service_id"]))

    api_data_cancellation["train_service_id"] = api_data_cancellation["service_uid"].map(
        service_uid_to_id)

    api_data_cancellation.dropna(
        subset=["train_service_id"], inplace=True)

    api_data_cancellation = api_data_cancellation.merge(
        database_data_train_stop,
        on="train_service_id",
        how="inner"
    )

    api_data_cancellation.drop(
        columns=["service_uid", "station_name",
                 "origin_name", "destination_name",
                 "cancelled", "train_service_id", "station_id"], inplace=True)

    api_data_cancellation = api_data_cancellation[[
        "train_stop_id", "cancel_reason"]]
    api_data_cancellation.rename(
        columns={"cancel_reason": "reason"}, inplace=True)

    database_data_cancellation = set(
        database_data_cancellation.itertuples(index=False, name=None))
    api_data_cancellation = set(
        api_data_cancellation.itertuples(index=False, name=None))
    new_cancellation = api_data_cancellation - database_data_cancellation

    return new_cancellation


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

    new_routes = find_new_routes(
        api_data_route, database_data_route, database_data_stations, database_data_operators)

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


def update_train_service(api_data: DataFrame, conn: Connection):
    """Updates database's train_service table."""
    api_data_train_service = api_data[[
        "service_uid", "train_identity", "service_date",
        "origin_name", "destination_name", "operator_name"
    ]].drop_duplicates()

    with conn.cursor() as cur:
        cur.execute(
            """SELECT service_uid,
                      train_identity,
                      service_date,
                      route_id
               FROM train_service;"""
        )
        rows = cur.fetchall()
        database_data_train_service = DataFrame(rows)

        cur.execute(
            "SELECT station_id, station_crs, station_name FROM station;")
        rows = cur.fetchall()
        database_data_stations = DataFrame(rows)

        cur.execute("SELECT operator_id, operator_name FROM operator;")
        rows = cur.fetchall()
        database_data_operators = DataFrame(rows)

        cur.execute(
            "SELECT route_id, origin_station_id, destination_station_id, operator_id FROM route;")
        rows = cur.fetchall()
        database_data_routes = DataFrame(rows)

    new_train_service = find_new_train_services(api_data_train_service,
                                                database_data_train_service,
                                                database_data_stations,
                                                database_data_operators,
                                                database_data_routes)

    if not new_train_service.empty:
        new_train_service_tuples = list(
            new_train_service.itertuples(index=False, name=None))
        logger.info("Updating train_service table with %s new train services.",
                    len(new_train_service_tuples))
        try:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO train_service (service_uid,
                                       train_identity,
                                       service_date,
                                       route_id) 
                    VALUES (%s, %s, %s, %s);
                    """,
                    new_train_service_tuples
                )
            conn.commit()
            logger.info("Train service table has been updated.")
        except DatabaseError as e:
            conn.rollback()
            logger.error("Database error: %s", e)
            raise
    else:
        logger.info("No new train services to add.")


def update_train_stop(api_data: DataFrame, conn: Connection):
    """Updates database's train_stop table."""
    api_data_train_stop = api_data[[
        "service_uid", "station_name", "scheduled_arr_time",
        "actual_arr_time", "scheduled_dep_time", "actual_dep_time",
        "platform", "platform_changed"
    ]].drop_duplicates()

    with conn.cursor() as cur:
        cur.execute("SELECT train_service_id, service_uid FROM train_service;")
        rows = cur.fetchall()
        database_data_train_services = DataFrame(rows)

        cur.execute("SELECT station_id, station_name FROM station;")
        rows = cur.fetchall()
        database_data_stations = DataFrame(rows)

    api_data_train_stop = map_api_train_stop_data(api_data_train_stop,
                                                  database_data_train_services,
                                                  database_data_stations)
    try:
        with conn.cursor() as cur:
            execute_batch(cur, """
                INSERT INTO train_stop (
                    train_service_id,
                    station_id,
                    scheduled_arr_time,
                    actual_arr_time,
                    scheduled_dep_time,
                    actual_dep_time,
                    platform,
                    platform_changed
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (train_service_id, station_id)
                DO UPDATE SET
                    scheduled_arr_time = EXCLUDED.scheduled_arr_time,
                    actual_arr_time = EXCLUDED.actual_arr_time,
                    scheduled_dep_time = EXCLUDED.scheduled_dep_time,
                    actual_dep_time = EXCLUDED.actual_dep_time,
                    platform = EXCLUDED.platform,
                    platform_changed = EXCLUDED.platform_changed;
            """, list(api_data_train_stop.itertuples(index=False, name=None)))

        conn.commit()
        logger.info("Updated %d rows into train_stop.",
                    len(api_data_train_stop))
    except DatabaseError as e:
        conn.rollback()
        logger.error("Database error during train_stop update: %s", e)
        raise


def update_cancellation(api_data: DataFrame, conn: Connection):
    """Updates database's cancellation table."""
    api_data_cancellation = api_data[[
        "service_uid", "station_name", "origin_name", "destination_name", "cancelled", "cancel_reason"
    ]].drop_duplicates()

    api_data_cancellation = api_data_cancellation[api_data_cancellation["cancelled"] == True]

    with conn.cursor() as cur:
        cur.execute("""
            SELECT train_stop_id,
                   reason
            FROM cancellation;
        """)
        rows = cur.fetchall()
        database_data_cancellation = DataFrame(rows)

        cur.execute("SELECT train_service_id, service_uid FROM train_service;")
        rows = cur.fetchall()
        database_data_train_services = DataFrame(rows)

        cur.execute("""
            SELECT train_stop_id, train_service_id, station_id
            FROM train_stop;
        """)
        rows = cur.fetchall()
        database_data_train_stop = DataFrame(rows)

    new_cancellation = find_new_cancellations(api_data_cancellation,
                                              database_data_cancellation,
                                              database_data_train_services,
                                              database_data_train_stop)

    if new_cancellation:
        new_cancellation_tuples = list(new_cancellation)
        logger.info("Updating cancellation table with %s new cancellations.",
                    len(new_cancellation_tuples))
        try:
            with conn.cursor() as cur:
                execute_batch(
                    cur,
                    """
                    INSERT INTO cancellation (train_stop_id, reason) 
                    VALUES (%s, %s);
                    """,
                    new_cancellation_tuples
                )
            conn.commit()
            logger.info("Cancellation table has been updated.")
        except DatabaseError as e:
            conn.rollback()
            logger.error("Database error: %s", e)
            raise
    else:
        logger.info("No new cancellations to add.")


def load_data_into_database(api_data: DataFrame,
                            conn: Connection) -> None:
    """Load data into the database. """
    update_station(api_data, conn)
    update_operator(api_data, conn)
    update_route(api_data, conn)
    update_train_service(api_data, conn)
    update_train_stop(api_data, conn)
    update_cancellation(api_data, conn)


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as db_connection:
        logger.info("Connection established.")
        stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
        fetched_data = fetch_train_data(stations)
        transformed_fetched_data = transform_train_data(fetched_data)
        load_data_into_database(transformed_fetched_data, db_connection)
