"""Lambda handler script for reports email script."""

import logging
from os import environ as ENV

from dotenv import load_dotenv

from extract_reports import get_db_connection, get_station_name_from_crs
from transform_summary import get_station_summary
from report import get_email_message_as_string
from load import load_new_report, get_s3_client
import boto3

logger = logging.getLogger()
logger.setLevel("DEBUG")

ses_client = boto3.client("ses", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                          aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
sns_client = boto3.client("sns", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                          aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
s3_client = get_s3_client()


def lambda_handler(event, context) -> dict:
    """AWS Lambda handler that runs the ETL pipeline for summary reports."""
    load_dotenv()
    try:
        logger.info("Lambda triggered, checking for existing PDF report in S3.")
        load_new_report(s3_client)
    except:
        ...
