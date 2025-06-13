"""Script for loading data into RDS."""

from logging import getLogger
from os import environ as ENV

import pandas as pd
from pandas import DataFrame

from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.extras import RealDictCursor


def get_connection():
    """Return a database connection."""
    conn = connect(
        dbname=ENV["DB_NAME"],
        user=ENV["DB_USER"],
        password=ENV["DB_PASSWORD"],
        host=ENV["DB_HOST"],
        port=ENV["DB_PORT"],
        cursor_factory=RealDictCursor
    )

    return conn


if __name__ == "__main__":
    load_dotenv()
    with get_connection() as db_connection:
        print("Connected to database.")
