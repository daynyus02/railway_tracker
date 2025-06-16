"""Main file that contains the ETL and lambda handler."""

import logging
from os import environ as ENV

from dotenv import load_dotenv

from extract import fetch_train_data
from transform import transform_train_data
from load import get_connection, load_data_into_database

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)

load_dotenv()
STATIONS = ENV["STATIONS"].split(",")


def run(stations: list[str]):
    """Run ETL."""
    with get_connection() as db_connection:
        fetched_data = fetch_train_data(stations)
        transformed_fetched_data = transform_train_data(fetched_data)
        load_data_into_database(transformed_fetched_data, db_connection)


def lambda_handler(event=None, context=None):
    """AWS Lambda handler that runs the ETL pipeline."""
    try:
        logger.info("Lambda triggered, running ETL.")
        run(STATIONS)
        return {
            "statusCode": 200,
            "body": "ETL completed."
        }
    except Exception as e:
        logger.exception("ETL failed.")
        return {
            "statusCode": 500,
            "body": f"ETL failed: {str(e)}"
        }


if __name__ == "__main__":
    run(STATIONS)
