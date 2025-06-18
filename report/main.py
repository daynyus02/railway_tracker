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


def lambda_handler(event, context) -> dict:
    """AWS Lambda handler that runs the ETL pipeline for summary reports."""
    load_dotenv()
    for station in stations:
        try:
            logger.info(
                "Lambda triggered, checking for existing PDF report in S3.")
            pdf = load_new_report(s3_client)
        except:
            logger.info("Error.")

    msg = get_email_message_as_string(station_name, pdf)
    response = ses_client.send_raw_email(
        Source=msg['From'],
        Destinations=[msg['To']],
        RawMessage={'Data': msg}
    )


if __name__ == "__main__":
    load_dotenv()

    s3_client = boto3.client(
        "s3", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    sns_client = boto3.client("sns", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    ses_client = boto3.client("sns", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
                              aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
    subs = sns_client.list_subscriptions_by_topic(
        TopicArn='arn:aws:sns:eu-west-2:129033205317:c17-trains-incidents-PAD-BRI')

    emails = [d["Endpoint"] for d in subs["Subscriptions"]]
