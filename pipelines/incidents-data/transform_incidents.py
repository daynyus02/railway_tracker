"""A script to transform data from the National Rail Incidents API."""

from os import environ as ENV
import logging
import re

from dotenv import load_dotenv
import pandas as pd

from extract_incidents import extract

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)

logger = logging.getLogger(__name__)


def is_paddington_to_bristol(text: str) -> bool:
    """Filters for trains between Paddington and Bristol Temple Meads."""
    pattern = r'(between|from) London Paddington (and|to) .*Bristol Temple Meads'
    return re.search(pattern, text, re.IGNORECASE) is not None


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Transform the data to be correct data types."""
    df = df.copy()

    logging.debug("Transform started.")
    df["start_time"] = pd.to_datetime(df["start_time"], utc=True)
    df["end_time"] = pd.to_datetime(df["end_time"], utc=True)
    df["is_planned"] = df["is_planned"].map(
        {"true": True, "false": False}).fillna(False)

    logging.debug(df.dtypes)

    df = df[df["routes_affected"].apply(is_paddington_to_bristol)]
    logger.info(
        "Found %s incidents between London Paddington and Bristol.", len(df))

    df.drop(columns=['routes_affected'])

    logger.info(df.head())

    return df


if __name__ == "__main__":
    load_dotenv()
    data = extract()
    transform(data)
