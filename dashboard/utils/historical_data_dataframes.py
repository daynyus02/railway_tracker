import pandas as pd
import streamlit as st

@st.cache_data
def get_unique_routes(data:pd.DataFrame):
    unique_routes = data[['origin_name', 'destination_name']].drop_duplicates()
    unique_routes_list = unique_routes.apply(
        lambda row: f"{row['origin_name']} to {row['destination_name']}", axis=1
    ).sort_values().tolist()
    return unique_routes_list

@st.cache_data
def get_cancellation_data_per_station(df:pd.DataFrame) -> pd.DataFrame:
    cancelled = df[["service_uid","station_name", "Status"]].copy()
    cancelled = cancelled.groupby(["station_name","Status"])["service_uid"].nunique().reset_index(name="Count")
    return cancelled[cancelled["Status"]=="Cancelled"].rename(columns={"station_name": "Station"})

@st.cache_data
def get_avg_delay_per_station(df: pd.DataFrame) -> pd.DataFrame:
    station_delays = df.groupby(["station_name"])["delay_time"].mean().reset_index().copy()
    station_delays["delay_time"] = station_delays["delay_time"].apply(lambda x: round(x, 1))
    return station_delays
