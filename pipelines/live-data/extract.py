"""Extracts train data from the Realtime Trains API."""
from os import environ as ENV
import logging

from dotenv import load_dotenv
import requests
import pandas as pd
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fetch_station_json(start_crs: str, end_crs: str) -> dict:
    """Fetches JSON data from the Realtime Trains API for a given CRS code."""
    if not isinstance(start_crs, str) and isinstance(end_crs, str):
        logger.error("Invalid CRS: %s. Expected a string.", crs)
        raise ValueError("The CRS must be a string.")
    url = f"https://api.rtt.io/api/v1/json/search/{start_crs}/to/{end_crs}"
    try:
        response = requests.get(url=url, auth=(ENV["API_USERNAME"], ENV["API_PASSWORD"]), timeout=5)
        logger.info("Successfully connected to '%s'", url)
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("Request failed for CRS %s: %s", crs, e)
        raise

def get_station_name(response: dict):
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
    if services == []:
        logger.debug("No services to retrieve.")
        return services
    logger.info("Train services successfully retrieved from API response.")
    return services

def extract_train_info(service: dict, name: str, crs: str) -> dict:
    """ Extracts key train information fields from a single service dictionary."""
    logger.debug("Extracting train info for services from %s", crs)
    location_detail = service.get("locationDetail", {})
    origin = location_detail.get("origin", [{}])[0]
    destination = location_detail.get("destination", [{}])[0]

    # service_info =  {'serviceUid': service.get('serviceUid'),
    #                 'train_identity': service.get("trainIdentity"),
    #                 'station_name': name,
    #                 'station_crs': crs,
    #                 'origin_name': origin.get("description"),
    #                 'destination_name': destination.get("description"),
    #                 'gbttBookedArrival': location_detail.get("gbttBookedArrival"),
    #                 'realtimeArrival': location_detail.get("realtimeArrival"),
    #                 'gbttBookedDeparture': location_detail.get("gbttBookedDeparture"),
    #                 'realtimeDeparture': location_detail.get("realtimeDeparture"),
    #                 'atocName': service.get("atocName"),
    #                 'runDate': service.get("runDate"),
    #                 'platform': location_detail.get("platform"),
    #                 'platform_changed': location_detail.get("platformChanged"),
    #                 'cancelled': bool(location_detail.get('cancelReasonCode')),
    #                 'cancel_reason': location_detail.get('cancelReasonLongText')
    #                 }
    service_info =  {'service_uid': service.get('serviceUid'),
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
                    'cancel_reason': location_detail.get('cancelReasonLongText')
                    }

    logger.info("Extracted train info for service '%s'", service_info.get('service_uid'))
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

def get_service_dataframe(start_crs:str, end_crs: str) -> pd.DataFrame:
    """Retrieves, processes, and returns train data as a dataframe for a given station CRS."""
    logger.debug("Retrieving service dataframe for service from %s - %s", start_crs, end_crs)
    data = fetch_station_json(start_crs, end_crs)
    trains = get_trains(data)
    name = get_station_name(data)
    trains_list = make_train_info_list(trains, name, start_crs)
    df = make_dataframe(trains_list)
    logger.info("Retrieved service dataframe for CRS: %s", start_crs)
    return df

def fetch_train_data(station_list: list[list]) -> pd.DataFrame:
    """Returns a dataframe of the services given a list of station crs."""
    logger.debug("Fetching service data for stations: %s", station_list)
    station_dfs = []
    for a,b in station_list:
        station_dfs.append(get_service_dataframe(a,b))
    aggregated_df = pd.concat(station_dfs, ignore_index=True)
    logger.info("Fetched service data for %d stations.", len(station_list))
    return aggregated_df

if __name__ == "__main__":
    load_dotenv()
    result = fetch_train_data([['PAD', 'BRI'], 
                               ['RDG', 'BRI'], 
                               ['DID', 'BRI'], 
                               ['SWI', 'BRI'],
                               ['CPM', 'BRI'],
                               ['BTH', 'BRI'],
                               ['BRI', 'PAD'], 
                               ['BTH', 'PAD'], 
                               ['CPM', 'PAD'], 
                               ['SWI', 'PAD'],
                               ['DID', 'PAD'],
                               ['RDG', 'PAD']])
    