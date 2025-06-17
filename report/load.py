"""Script for loading reports into S3 bucket."""

from os import environ as ENV
import logging

from boto3 import client
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="WARNING",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def get_s3_client() -> client:
    """Returns an S3 client using boto3."""

    s3_client = client(
        "s3", aws_access_key_id=ENV["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])

    return s3_client


def report_already_exists(bucket_name: str, filename: str) -> bool:
    """Returns true if a file with the given filename already exists in S3 bucket."""
