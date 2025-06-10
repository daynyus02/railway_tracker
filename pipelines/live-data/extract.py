"""Extracts train data from the Realtime Trains API."""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import requests
import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_station_json(crs: str) -> dict:
    """Fetches JSON data from the Realtime Trains API for a given CRS code."""
    if not isinstance(crs, str):
        logger.error("Invalid CRS: %s. Expected a string.", crs)
        raise ValueError("The CRS must be a string.")
    url = f"https://api.rtt.io/api/v1/json/search/{crs}"
    try:
        response = requests.get(url=url, auth=(ENV["API_USERNAME"], ENV["API_PASSWORD"]), timeout=5)
        logger.info("Successfully fetched data for CRS: %s", crs)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request failed for CRS %s: %s", crs, e)
        raise

def get_station_name(response: dict):
    """Returns the station name from the api response."""
    location = response.get('location')
    if location:
        name = location.get('name', 'Unknown')
        logger.info("Extracted station name: %s", name)
        return name
    logger.warning("No location data found in response.")
    return None

def get_trains(response: dict) -> list[dict]:
    """Extracts the list of train services from the API response."""
    services = response.get('services', [])
    logger.info("Train services successfully retrieved from API response.")
    return services

def extract_train_info(service: dict, name: str, crs: str) -> dict:
    """ Extracts key train information fields from a single service dictionary."""
    logger.debug("Extracting train info for services at %s", crs)
    location_detail = service.get("locationDetail", {})
    origin = location_detail.get("origin", [{}])[0]
    destination = location_detail.get("destination", [{}])[0]

    service_info =  {'serviceUid': service.get('serviceUid'),
            'station_name': name,
            'station_crs': crs,
            'origin_name': origin.get("description", ""),
            'origin_tiploc': origin.get("tiploc", ""),
            'destination_name': destination.get("description", ""),
            'destination_tiploc': destination.get("tiploc", ""),
            'realtimeActivated': location_detail.get("realtimeActivated", False),
            'gbttBookedDeparture': location_detail.get("gbttBookedDeparture", ""),
            'isCall': location_detail.get("isCall", False),
            'realtimeDeparture': location_detail.get("realtimeDeparture", ""),
            'atocName': service.get("atocName", ""),
            'runDate': service.get("runDate", ""),
            'displayAs': location_detail.get("displayAs", "")
            }
    logger.info("Extracted train info for service '%s'", service_info.get('serviceUid'))
    return service_info

def make_train_info_list(train_list: list[dict], name:str, crs: str) -> list[dict]:
    """Processes a list of train services to extract structured information."""
    return [extract_train_info(train, name, crs) for train in train_list]

def make_dataframe(train_data: list[dict]) -> pd.DataFrame:
    """Converts a list of train information dictionaries into a pandas DataFrame."""
    logger.debug("Creating dataframe from service data.")
    df = pd.DataFrame(train_data)
    logger.info("Created dataframe with %d records.", len(df))
    return df

def get_service_dataframe(crs:str) -> pd.DataFrame:
    """Retrieves, processes, and returns train data as a dataframe for a given station CRS."""
    logger.debug("Retrieving service dataframe for CRS: %s", crs)
    data = fetch_station_json(crs)
    trains = get_trains(data)
    name = get_station_name(data)
    trains_list = make_train_info_list(trains, name, crs)
    df = make_dataframe(trains_list)
    logger.info("Retrieved service dataframe for CRS: %s", crs)
    return df

def fetch_train_data(station_list: list[str]) -> pd.DataFrame:
    """Returns a dataframe of the services given a list of station crs."""
    logger.debug("Fetching service data for stations: %s", station_list)
    station_dfs = []
    for crs in station_list:
        station_dfs.append(get_service_dataframe(crs))
    aggregated_df = pd.concat(station_dfs, ignore_index=True)
    logger.info("Fetched service data for %d stations.", len(station_list))
    return aggregated_df

if __name__ == "__main__":
    load_dotenv()
    df = fetch_train_data(['LTV'])
    print(df)