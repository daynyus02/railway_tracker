"""A script with functions to send incident alerts to SNS topics."""

from os import environ as ENV
import logging

from boto3 import client
from botocore.exceptions import ClientError
from pandas import Timestamp

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


def get_sns_client():
    """Returns a boto3 SNS client."""
    return client("sns",
                  aws_access_key_id=ENV["ACCESS_KEY"],
                  aws_secret_access_key=ENV["SECRET_KEY"],
                  region_name=ENV["REGION"])


def get_sns_topic_arn(sns_client, origin_crs: str, destination_crs: str) -> str:
    """Returns the arn for the alerts topic."""
    response = sns_client.create_topic(
        Name=f"c17-trains-incidents-{origin_crs}-{destination_crs}")
    return response["TopicArn"]


def publish_incident_alert_to_topic(origin_crs: str, destination_crs: str, summary: str,
                                    info_link: str, start_time: Timestamp, end_time: Timestamp,
                                    is_planned: bool, new: bool) -> None:
    """Publish a new or updated incident alert to a topic."""
    sns = get_sns_client()
    topic_arn = get_sns_topic_arn(sns, origin_crs, destination_crs)
    start_time = start_time.tz_convert("Europe/London").tz_localize(None)

    if new:
        subject = "New "
    else:
        subject = "There has been an update to an "

    subject += f"incident on route {origin_crs} to {destination_crs} from {start_time.date()}."
    message = f"{summary}.\n\nThe incident will take place from {start_time}"

    if is_planned:
        end_time = end_time.tz_convert("Europe/London").tz_localize(None)
        message += f" until {end_time}."
    else:
        message += "."

    message += f"\n\nFor more information, please visit {info_link}."

    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject=subject
        )
        logger.info("Successfully published alert.")
    except ClientError as e:
        logger.error("Failed to publish alert: %s",
                     e.response['Error']['Message'])
