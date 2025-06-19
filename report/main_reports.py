"""Lambda handler script for reports email script."""

import logging
from os import environ as ENV

from dotenv import load_dotenv

import boto3
from pandas import DataFrame
from botocore.exceptions import ClientError
from psycopg2.extensions import connection as Connection
from psycopg2.extras import DictCursor

from extract_reports import get_db_connection, get_days_data_per_station
from transform_summary import get_station_summary
from report import generate_pdf, get_email_message_as_string
from load import load_new_report, get_s3_client

logger = logging.getLogger()
logger.setLevel("DEBUG")


def get_station_name_crs_tuples(conn: Connection) -> list[str]:
    """Retrieves name and crs for each station in the database as list of tuples."""

    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute("SELECT station_name, station_crs FROM station;")
        station_names = curs.fetchall()

    return station_names


def get_sns_topic_arn_by_station(sns_client: "Client", station_crs: str) -> str:
    """Returns the arn for the relevant AWS SNS topic per station."""

    response = sns_client.create_topic(
        Name=f"c17-trains-reports-{station_crs}")
    return response["TopicArn"]


def get_subscriber_emails_from_topic(sns_client: "Client", arn: str) -> list[str]:
    """Gets a list of emails subscribed to an AWS SNS topic."""

    subs = sns_client.list_subscriptions_by_topic(
        TopicArn=arn)

    return [sub["Endpoint"] for sub in subs["Subscriptions"]]


def send_report_emails(ses_client: "Client", emails: list[str], msg: bytes) -> dict:
    """Sends summary report emails to specified recipients."""

    for email in emails:
        try:
            ses_client.send_raw_email(
                Source="trainee.stefan.cole@sigmalabs.co.uk",
                Destinations=[email],
                RawMessage={"Data": msg.as_string()}
            )
            logging.info(
                "Successfully sent summary report email.")
        except ClientError as e:
            logging.error(
                "Failed to send summary report email.")
            return {
                "statusCode": 500,
                "body": f"Error sending summary report email: {str(e)}."
            }

        return {
            "statusCode": 200,
            "body": "Summary report emails successfully sent."
        }


def lambda_handler(event, context) -> dict:
    """AWS Lambda handler that runs the ETL pipeline for summary reports."""
    load_dotenv()

    s3_client = get_s3_client()
    sns_client = boto3.client("sns", aws_access_key_id=ENV["ACCESS_KEY"],
                              aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])
    ses_client = boto3.client("ses", aws_access_key_id=ENV["ACCESS_KEY"],
                              aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])

    with get_db_connection() as conn:
        stations = get_station_name_crs_tuples(conn)

        for station in stations:
            data = get_days_data_per_station(station[1], conn)
            if data:
                transformed_data = get_station_summary(DataFrame(data))

                report = generate_pdf(station[0], transformed_data)
                load_new_report(s3_client, station[0], transformed_data)
                msg = get_email_message_as_string(station[0], report)

                topic_arn = get_sns_topic_arn_by_station(
                    sns_client, station[1])
                emails = get_subscriber_emails_from_topic(
                    sns_client, topic_arn)

                if emails:
                    sent_status = send_report_emails(ses_client, emails, msg)
                    logging.info("%s", sent_status)
