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
        cur.execute("""
            SELECT train_service_id,
                   station_id,
                   scheduled_arr_time,
                   actual_arr_time,
                   scheduled_dep_time,
                   actual_dep_time,
                   platform,
                   platform_changed
            FROM train_stop;     
            """
                    )
        rows = cur.fetchall()
        database_data_train_stop = DataFrame(rows)

        cur.execute("SELECT train_service_id, service_uid FROM train_service;")
        rows = cur.fetchall()
        database_data_train_services = DataFrame(rows)

        cur.execute("SELECT station_id, station_name FROM station;")
        rows = cur.fetchall()
        database_data_stations = DataFrame(rows)

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

    db_stop_dict = {
        (row.train_service_id, row.station_id): row
        for row in database_data_train_stop.itertuples(index=False)
    }

    inserts = []
    updates = []

    for row in api_data_train_stop.itertuples(index=False):
        key = (row.train_service_id, row.station_id)
        api_values = row[2:]
        if key not in db_stop_dict:
            inserts.append((
                row.train_service_id,
                row.station_id,
                row.scheduled_arr_time,
                row.actual_arr_time,
                row.scheduled_dep_time,
                row.actual_dep_time,
                row.platform,
                row.platform_changed
            ))
        else:
            db_row = db_stop_dict[key]
            db_values = db_row[2:]
            if api_values != db_values:
                updates.append((
                    row.train_service_id,
                    row.station_id,
                    row.scheduled_arr_time,
                    row.actual_arr_time,
                    row.scheduled_dep_time,
                    row.actual_dep_time,
                    row.platform,
                    row.platform_changed
                ))

    try:
        with conn.cursor() as cur:
            if inserts:
                execute_batch(cur, """
                    INSERT INTO train_stop (
                        train_service_id, station_id,
                        scheduled_arr_time, actual_arr_time,
                        scheduled_dep_time, actual_dep_time,
                        platform, platform_changed
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """, inserts)
                logger.info("Inserted %d new train_stop rows.", len(inserts))

            if updates:
                execute_batch(cur, """
                    UPDATE train_stop SET
                        scheduled_arr_time = %s,
                        actual_arr_time = %s,
                        scheduled_dep_time = %s,
                        actual_dep_time = %s,
                        platform = %s,
                        platform_changed = %s
                    WHERE train_service_id = %s AND station_id = %s;
                """, [(
                    r[2],  # scheduled_arr_time
                    r[3],  # actual_arr_time
                    r[4],  # scheduled_dep_time
                    r[5],  # actual_dep_time
                    r[6],  # platform
                    r[7],  # platform_changed
                    r[0],  # train_service_id
                    r[1]   # station_id
                )
                    for r in updates])
                logger.info(
                    "Updated %d existing train_stop rows.", len(updates))

        conn.commit()
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
        database_train_data = load_data_from_database(db_connection)
        load_data_into_database(transformed_fetched_data, db_connection)
