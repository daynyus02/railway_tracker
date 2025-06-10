"""Extracts train data from the Realtime Trains API."""
import requests
from os import environ as ENV
from dotenv import load_dotenv
import pandas as pd

def fetch_station_json(crs: str) -> dict:
    """Fetches JSON data from the Realtime Trains API for a given CRS code."""
    if not isinstance(crs, str):
        raise ValueError("The CRS must be a string.")
    url = f"https://api.rtt.io/api/v1/json/search/{crs}"
    response = requests.get(url=url, auth=(ENV["API_USERNAME"], ENV["API_PASSWORD"]))
    return response.json()

def get_trains(response: dict) -> list[dict]:
    """Extracts the list of train services from the API response."""
    return response['services']

def extract_train_info(response: dict) -> dict:
    """ Extracts key train information fields from a single service dictionary."""
    location_detail = response.get("locationDetail", {})
    origin = location_detail.get("origin", [{}])[0]
    destination = location_detail.get("destination", [{}])[0]
    
    return {"station_name": '',
            "station_tiploc": '',
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

def make_train_info_list(train_list: list[dict]) -> list[dict]:
    """Processes a list of train services to extract structured information."""
    return [extract_train_info(train) for train in train_list]

def make_dataframe(train_data: list[dict]) -> pd.DataFrame:
    """Converts a list of train information dictionaries into a pandas DataFrame."""
    return pd.DataFrame(train_data)

def get_service_dataframe(crs:str) -> pd.DataFrame:
    """Retrieves, processes, and returns train data as a dataframe for a given station CRS."""
    data = fetch_station_json(crs)
    trains = get_trains(data)
    trains_list = make_train_info_list(trains)
    return make_dataframe(trains_list)

def fetch_train_data(station_list: list[str]) -> pd.DataFrame:
    station_dfs = []
    for crs in station_list:
        station_dfs.append(get_service_dataframe(crs))
    return pd.concat(station_dfs, ignore_index=True)

if __name__ == "__main__":
    load_dotenv()
    response = fetch_station_json('LTV')
    print(get_trains(response))
    