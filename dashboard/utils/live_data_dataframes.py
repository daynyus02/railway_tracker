"""Data manipulation functions for the live dashboard."""
from os import environ as ENV
import pandas as pd
import numpy as np
import streamlit as st
import psycopg2
from dotenv import load_dotenv

def get_connection():
    """Returns a psycopg2 connection to the RDS database."""
    load_dotenv()
    connection = psycopg2.connect(host=ENV['DB_HOST'],
                            port=ENV['DB_PORT'],
                            dbname=ENV['DB_NAME'],
                            user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'])
    return connection

@st.cache_resource
def fetch_data(query, _conn) -> pd.DataFrame:
    """Returns a dataframe given a query and connection."""
    df = pd.read_sql_query(query, _conn)
    _conn.close()
    return df

### Transforming data ###
def convert_times_to_datetime(df) -> None:
    """Converts date columns to datetime."""
    for col in ['actual_arr_time','scheduled_arr_time', 'actual_dep_time','scheduled_dep_time']:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%H:%M:%S')

def add_status_column(df) -> None:
    """Adds a column containing service status based on scheduled and actual times."""
    conditions = [(df['cancelled'] == True),
                (df['scheduled_dep_time'] < df['actual_dep_time'])]
    choices = ['Cancelled', 'Delayed']
    df['Status'] = np.select(conditions, choices, default="On Time")

def filter_data(df: pd.DataFrame, selected_arrival: str, selected_destination:str, selected_operator: str) -> pd.DataFrame:
    """Filters services in a df given the time and operator parameters."""
    filtered_data = df.copy()

    if selected_arrival != "All":
        filtered_data = filtered_data[filtered_data["station_name"] == selected_arrival]

    if selected_destination != "All":
        filtered_data = filtered_data[filtered_data["destination_name"] == selected_destination]

    if selected_operator != "All":
        filtered_data = filtered_data[filtered_data["operator_name"] == selected_operator]
    return filtered_data

### Displaying delay info ###
@st.cache_data
def get_delays(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a df of only delayed trains."""
    delays = df[["Status",
                 "service_uid",
                 "scheduled_dep_time",
                 "actual_dep_time", 
                 "station_name",
                 "origin_name",
                 "destination_name", 
                 "operator_name"
                ]].copy()
    delays = delays[delays["Status"] == "Delayed"]
    return delays

def add_delay_time(df: pd.DataFrame) -> None:
    """Adds a delay time column containing the delay in minutes."""
    df["delay_time"] = df["actual_dep_time"] - df["scheduled_dep_time"]
    df = df[df["delay_time"] > pd.Timedelta(0)]
    df = df.dropna(subset=["delay_time"])
    df["delay_time"] = df["delay_time"].dt.total_seconds() // 60
    return df

@st.cache_data
def get_cancelled_data_per_operator(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a df containing the cancellation count per operator."""
    cancelled = df[["service_uid","operator_name", "Status"]].copy()
    cancelled = cancelled.groupby(["operator_name","Status"])["service_uid"].nunique().reset_index(name="Count")
    return cancelled[cancelled["Status"]=="Cancelled"].rename(columns={"operator_name": "Operator"})

@st.cache_data
def get_interruption_data(df:pd.DataFrame) -> pd.DataFrame:
    """Returns a df with the number of unique cancelled services per operator."""
    interruptions = df[["service_uid","operator_name", "Status"]].copy()
    interruptions = interruptions.groupby(["operator_name", "Status"])["service_uid"].nunique().reset_index()
    interruptions["percentage_of_trains"] = (interruptions["service_uid"]*100 / interruptions.groupby('operator_name')['service_uid'].transform('sum')).round(1)
    return interruptions

@st.cache_data
def get_route_data(df:pd.DataFrame) -> pd.DataFrame:
    """Aggregates delay count and average delay time per origin-destination pair."""
    routes = df.groupby(["origin_name", "destination_name"]).agg(
        delayed_count=("delay_time", "size"),
        avg_delay_time=("delay_time", "mean")
    ).reset_index()

    routes["avg_delay_time"] = routes["avg_delay_time"].round(1)

    routes.rename(columns={
        'origin_name': 'Origin',
        'destination_name': 'Destination',
        'delayed_count': 'Number of Delays',
        'avg_delay_time': 'Average Delay (min)'
    }, inplace=True)
    return routes

if __name__ == '__main__':
    pass
