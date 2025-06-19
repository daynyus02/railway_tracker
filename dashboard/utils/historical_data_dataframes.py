"""Data manipulation functions for the Historical Data page."""
import pandas as pd
import streamlit as st

@st.cache_resource
def fetch_data(_connection)-> pd.DataFrame:
    """Fetches all service data from the RDS"""
    query = """SELECT *
               FROM train_info_view;"""
    data = pd.read_sql_query(query, _connection)
    _connection.close()
    return data

def station_to_crs(station_name: str) -> str:
    """Converts a full station name to its CRS"""
    crs_codes = {
    "London Paddington": "PAD",
    "Ealing Broadway": "EAL",
    "Slough": "SLO",
    "Maidenhead": "MAI",
    "Twyford": "TWY",
    "Reading": "RDG",
    "Tilehurst": "TLH",
    "Pangbourne": "PAN",
    "Goring & Streatley": "GOR",
    "Cholsey": "CHO",
    "Didcot Parkway": "DID",
    "Swindon": "SWI",
    "Chippenham": "CPM",
    "Melksham": "MKM",
    "Trowbridge": "TRO",
    "Westbury": "WSB",
    "Bradford-on-Avon": "BOA",
    "Bath Spa": "BTH",
    "Oldfield Park": "OLF",
    "Keynsham": "KYN",
    "Bristol Temple Meads": "BRI",
    "Bristol Parkway": "BPW"
}
    return crs_codes.get(station_name)

@st.cache_data
def get_unique_routes(df:pd.DataFrame) -> list[str]:
    """Retrieves all unique origin and destination station pairs from the dataframe"""
    unique_routes = df[['origin_name', 'destination_name']].drop_duplicates()
    unique_routes_list = unique_routes.apply(
        lambda row: f"{row['origin_name']} to {row['destination_name']}", axis=1
    ).sort_values().tolist()
    return unique_routes_list

@st.cache_data
def get_cancellation_data_per_station(df:pd.DataFrame) -> pd.DataFrame:
    """Returns a dataframe with cancelled service counts per station"""
    cancelled = df[["service_uid","station_name", "Status"]].copy()
    cancelled = cancelled.groupby(["station_name","Status"])["service_uid"].nunique().reset_index(name="Count")
    return cancelled[cancelled["Status"]=="Cancelled"].rename(columns={"station_name": "Station"})

@st.cache_data
def get_avg_delay_per_station(df: pd.DataFrame) -> pd.DataFrame:
    """Adds a column to a dataframe containing the average delay time per station"""
    station_delays = df.groupby(["station_name"])["delay_time"].mean().reset_index().copy()
    station_delays["delay_time"] = station_delays["delay_time"].apply(lambda x: round(x, 1))
    return station_delays

@st.cache_data
def get_unique_stations(df:pd.DataFrame) -> list[str]:
    """Retrieves all unique stations from the dataframe"""
    return df['station_name'].drop_duplicates().sort_values(ascending=True).tolist()
