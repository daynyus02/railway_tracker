"""A script with functions to send incident alerts to SNS topics."""

from os import environ as ENV
import logging

from dotenv import load_dotenv
from boto3 import client
from botocore.exceptions import ClientError

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def get_sns_client():
    """Returns a boto3 SNS client."""
    return client("sns",
                  aws_access_key_id=ENV["ACCESS_KEY"],
                  aws_secret_access_key=ENV["SECRET_KEY"],
                  region_name=ENV["REGION"])


def get_sns_topic_arn(sns_client, origin_crs: str, destination_crs: str) -> str:
    """Returns the arn for the alerts topic."""
    response = sns_client.create_topic(
        f"c17-trains-incidents-{origin_crs}-{destination_crs}")
    return response["TopicArn"]


def publish_to_topic_new(origin_crs: str, destination_crs: str, summary: str,
                         start_time: str, end_time: str, is_planned: bool) -> None:
    """Publish a new incident alert to a topic."""
    sns = get_sns_client()
    topic_arn = get_sns_topic_arn(sns, origin_crs, destination_crs)
    logger.info("Topic arn: %s.", topic_arn)

    subject = f"New incident on route {origin_crs} to {destination_crs} from {start_time}"
    message = summary

    if is_planned:
        subject += f" to {end_time}."
    else:
        subject += "."

    logger.info("Subject: %s.", subject)
    logger.info("Message: %s.", message)

    try:
        sns.publish(
            TopicArn=topic_arn,
            message=message,
            subject=subject
        )
        logger.info("Successfully published alert.")
    except ClientError as e:
        logger.error("Failed to publish alert.")


if __name__ == "__main__":
    load_dotenv()
    get_sns_client()
