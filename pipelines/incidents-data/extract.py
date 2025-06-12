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
    return response


def is_paddington_to_bristol(text: str) -> bool:
    """Filters for trains between Paddington and Bristol Temple Meads."""
    pattern = r'between London Paddington and .*Bristol Temple Meads'
    return re.search(pattern, text, re.IGNORECASE) != None


def extract_relevant_data(namespace: dict, incident_xml: ET) -> dict:
    """Extract data from an incident xml and store it in a dict."""
    incident_number = incident_xml.findtext(
        "inc:IncidentNumber", namespaces=namespace)
    version_number = incident_xml.findtext("inc:Version", namespaces=namespace)
    is_planned = incident_xml.findtext("inc:Planned", namespaces=namespace)

    incident_data = {
        "incident_number": incident_number,
        "version_number": version_number,
        "is_planned": is_planned
    }
    logger.debug("Incident data: %s", incident_data)
    return incident_data


def parse_xml(response: requests.Response) -> list[dict]:
    """Parse the XML response and filter incidents affecting Paddington to Bristol."""
    incidents = []

    ns = {
        'inc': 'http://nationalrail.co.uk/xml/incident',
        'com': 'http://nationalrail.co.uk/xml/common'
    }

    root = ET.fromstring(response.text)

    for incident in root.findall("inc:PtIncident", namespaces=ns):
        routes_affected = incident.find(
            "inc:Affects/inc:RoutesAffected", namespaces=ns)
        routes_text = "".join(routes_affected.itertext()).strip()

        if is_paddington_to_bristol(routes_text):
            logger.debug("Paddington to Bristol found: %s", routes_text)
            data = extract_relevant_data(ns, incident)
            incidents.append(data)

    return incidents


if __name__ == "__main__":
    load_dotenv()

    res = fetch_incident_data()

    parse_xml(res)
