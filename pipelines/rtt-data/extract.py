"""Extracts train data from the Realtime Trains API."""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import requests
from pandas import DataFrame, concat

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def fetch_station_json(crs: str) -> dict:
    """Fetches JSON data from the Realtime Trains API for a given CRS code."""
    if not isinstance(crs, str):
        logger.error("Invalid CRS: %s. Expected a string.", crs)
        raise ValueError("The CRS must be a string.")
    url = f"https://api.rtt.io/api/v1/json/search/{crs}"
    try:
        response = requests.get(url=url, auth=(
            ENV["API_USERNAME"], ENV["API_PASSWORD"]), timeout=5)
        logger.info("Successfully connected to '%s'", url)
        return response.json()
    except requests.exceptions.RequestException:
        logger.exception("Request failed for CRS: %s.", crs)
        raise


def get_station_name(response: dict) -> str | None:
    """Returns the station name from the api response."""
    location = response.get('location')
    if location:
        name = location.get('name')
        logger.info("Extracted station name: %s", name)
        return name
    logger.warning("No location data found in response.")
    return None


def get_trains(response: dict) -> list[dict]:
    """Extracts the list of train services from the API response."""
    services = response.get('services', [])
    if not services:
        logger.debug("No services to retrieve.")
    logger.info("Train services successfully retrieved from API.")
    return services


def extract_train_info(service: dict, name: str, crs: str) -> dict:
    """Extracts key train information fields from a single service dictionary."""
    logger.info("Extracting train info for services from %s", crs)
    location_detail = service.get("locationDetail", {})
    origin = location_detail.get("origin", [{}])[0]
    destination = location_detail.get("destination", [{}])[0]

    service_info = {'service_uid': service.get('serviceUid'),
                    'train_identity': service.get("trainIdentity"),
                    'station_name': name,
                    'station_crs': crs,
                    'origin_name': origin.get("description"),
                    'destination_name': destination.get("description"),
                    'scheduled_arr_time': location_detail.get("gbttBookedArrival"),
                    'actual_arr_time': location_detail.get("realtimeArrival"),
                    'scheduled_dep_time': location_detail.get("gbttBookedDeparture"),
                    'actual_dep_time': location_detail.get("realtimeDeparture"),
                    'operator_name': service.get("atocName"),
                    'service_date': service.get("runDate"),
                    'platform': location_detail.get("platform"),
                    'platform_changed': location_detail.get("platformChanged"),
                    'cancelled': bool(location_detail.get('cancelReasonCode')),
                    'cancel_reason': location_detail.get('cancelReasonLongText'),
                    'service_type': service.get("serviceType")
                    }

    logger.info("Extracted train info for service '%s'",
                service_info.get('service_uid'))
    return service_info


def make_train_info_list(train_list: list[dict] | None, name: str, crs: str) -> list[dict]:
    """Processes a list of train services to extract structured information."""
    if not train_list:
        logger.warning("No train data found for station: %s (%s)", name, crs)
        return []
    return [extract_train_info(train, name, crs) for train in train_list]


def get_service_dataframe(crs: str) -> DataFrame:
    """Retrieves, processes, and returns train data as a dataframe for a given station CRS."""
    logger.debug("Retrieving service dataframe for services at %s.", crs)
    data = fetch_station_json(crs)
    trains = get_trains(data)
    name = get_station_name(data)
    trains_list = make_train_info_list(trains, name, crs)
    df = DataFrame(trains_list)
    logger.info("Created dataframe for %s with %d records.", crs, len(df))
    return df


def fetch_train_data(station_list: list[list]) -> DataFrame:
    """Returns a dataframe of services from the stations in a given list."""
    logger.debug("Fetching service data for stations: %s", station_list)
    station_dfs = []
    for station in station_list:
        station_dfs.append(get_service_dataframe(station))
    aggregated_df = concat(station_dfs, ignore_index=True)
    logger.info("Fetched service data for %d stations.", len(station_list))
    return aggregated_df


if __name__ == "__main__":
    load_dotenv()
    stations = ['PAD', 'RDG', 'DID', 'SWI', 'CPM', 'BTH', 'BRI']
    result = fetch_train_data(stations)
