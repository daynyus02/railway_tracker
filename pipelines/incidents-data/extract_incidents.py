"""A script to extract data from the National Rail Incidents API.
Only extracting for Great Western Railway Services."""

from os import environ as ENV
import logging
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
import requests
from requests import Response
import pandas as pd

logger = logging.getLogger(__name__)

logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S"
)


def get_incident_data() -> Response:
    """Fetches data from API."""
    logger.debug("Sending request to API.")
    response = requests.get(ENV["GW_URL"], timeout=5)
    logger.info("Response status code: %s", response.status_code)
    return response


def extract_relevant_data(namespace: dict, incident_xml: ET) -> dict:
    """Extract data from an incident xml and store it in a dict."""
    logger.debug("Beginning extraction for incident.")

    incident_number = incident_xml.findtext(
        "inc:IncidentNumber", namespaces=namespace)
    version_number = incident_xml.findtext("inc:Version", namespaces=namespace)
    is_planned = incident_xml.findtext("inc:Planned", namespaces=namespace)
    start_time = incident_xml.findtext(
        "inc:ValidityPeriod/com:StartTime", namespaces=namespace)
    end_time = incident_xml.findtext(
        "inc:ValidityPeriod/com:EndTime", default="", namespaces=namespace)
    summary = "".join(incident_xml.find(
        "inc:Summary", namespaces=namespace).itertext()).strip()
    description = "".join(incident_xml.find(
        "inc:Description", namespaces=namespace).itertext()).strip()
    info_link = incident_xml.find(
        "inc:InfoLinks/inc:InfoLink/inc:Uri", namespaces=namespace).text.strip()

    routes_affected = "".join(incident_xml.find(
        "inc:Affects/inc:RoutesAffected", namespaces=namespace).itertext()).strip()

    incident_data = {
        "start_time": start_time,
        "end_time": end_time,
        "description": description,
        "incident_number": incident_number,
        "version_number": version_number,
        "is_planned": is_planned,
        "info_link": info_link,
        "summary": summary,
        "routes_affected": routes_affected
    }
    logger.info("Incident data: %s", incident_data)
    return incident_data


def parse_xml(response: Response) -> list[dict]:
    """Parse the XML response and return incidents."""
    incidents = []

    ns = {
        'inc': 'http://nationalrail.co.uk/xml/incident',
        'com': 'http://nationalrail.co.uk/xml/common'
    }

    root = ET.fromstring(response.text)

    for incident in root.findall("inc:PtIncident", namespaces=ns):
        incident_data = extract_relevant_data(ns, incident)
        incidents.append(incident_data)

    return incidents


def extract() -> pd.DataFrame:
    """Run extract process to get data from XML, and return it as a pandas dataframe."""
    res = get_incident_data()
    incidents = parse_xml(res)
    return pd.DataFrame(incidents)


if __name__ == "__main__":
    load_dotenv()

    data = extract()
    logging.info("Extracted DataFrame: %s", data)
