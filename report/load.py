"""Script for loading reports into S3 bucket."""

from os import environ as ENV
import logging
from datetime import datetime as dt

from boto3 import client
from botocore.exceptions import ClientError
from dotenv import load_dotenv
from pandas import DataFrame

from report.extract_reports import get_days_data_per_station, get_db_connection, get_station_name_from_crs
from transform_summary import get_station_summary
from report import generate_pdf

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="WARNING",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def get_s3_client() -> client:
    """Returns an S3 client using boto3."""
    try:
        s3_client = client(
            "s3", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
        logging.info("Successfully created S3 client.")
    except ClientError:
        logging.error("Failed to create S3 client.")

    return s3_client


def report_already_exists(s3_client: client, filename: str) -> bool:
    """Returns true if a file with the given filename already exists in S3 bucket."""

    try:
        s3_client.head_object(Bucket=ENV["S3_BUCKET_NAME"], Key=filename)
        logging.info("Report with filename %s exists.", filename)
        return True

    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey' or e.response['Error']['Code'] == '404':
            logger.info("%s does not already exist in S3")
            return False
        logger.error(
            "Error accessing S3 bucket to check for existing file.")
        raise


def load_new_report(s3_client: client, station_name: str, data: dict) -> None:
    """Loads a report to S3 if it does not already exist."""

    date_string = dt.today().strftime("%d-%m-%Y")

    filename = f"{station_name.lower().replace(" ", "_")}_summary_report_{date_string}.pdf"

    if not report_already_exists(s3_client, filename):
        pdf = generate_pdf(station_name, data)
        s3_client.put_object(
            Bucket=ENV["S3_BUCKET_NAME"], Key=filename, Body=pdf, ContentType='application/pdf')
        logger.info("%s file successfully created in S3.", filename)


if __name__ == "__main__":
    load_dotenv()

    with get_db_connection() as conn:
        extracted_data = DataFrame(get_days_data_per_station("DID", conn))
        summary_data = get_station_summary(extracted_data)

        station_name = get_station_name_from_crs("DID", conn)

        s3_client = get_s3_client()
        load_new_report(s3_client, station_name, summary_data)
