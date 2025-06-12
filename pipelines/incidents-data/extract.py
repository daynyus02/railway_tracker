"""A script to extract data from the National Rail Incidents API for Great Western Railway Services."""

from os import environ as ENV
import logging
import xml.etree.ElementTree as ET
import re

from dotenv import load_dotenv
import requests
import pandas

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def fetch_incident_data() -> requests.Response:
    """Fetches data from API."""
    logger.debug("Sending request to API.")
    response = requests.get(ENV["GW_URL"])
    logger.debug("Response status code: %s", response.status_code)
    logger.debug("Output: %s", response.text[:1000])
    return response


def is_paddington_to_bristol(text: str) -> bool:
    pattern = r'between London Paddington and .*Bristol Temple Meads'
    return re.search(pattern, text, re.IGNORECASE) != None


def parse_xml(response: requests.Response):
    """Parse the XML response into ."""
    root = ET.fromstring(response.text)


if __name__ == "__main__":
    load_dotenv()

    res = fetch_incident_data()

    parse_xml(res)
