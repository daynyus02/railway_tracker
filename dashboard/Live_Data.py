from os import environ as ENV
import pandas as pd
from dotenv import load_dotenv
import streamlit as st
import psycopg2

# conn = psycopg2.connect(host=ENV['DB_HOST'],
#                         port=ENV['DB_PORT'],
#                         dbname=ENV['DB_NAME'],
#                         user=ENV['DB_USER'],
#                         password=ENV['DB_PASSWORD'])

st.set_page_config(
    page_title="Railway Tracker",
    page_icon="🚆",
    layout="wide"
)

draft_data = pd.read_csv("example_data.csv")
draft_data = draft_data[draft_data["service_type"] == 'train']
draft_data = draft_data.dropna(subset=["actual_arr_time"])

st.title("Railway Tracker 🚆")

arrival_stations = sorted(draft_data["station_name"].unique())
destination_stations = sorted(draft_data["destination_name"].unique())
operators = sorted(draft_data["operator_name"].unique())

col1, col2, col3 = st.columns(3)
with col1:
    selected_arrival = st.selectbox("Arrival", options=["All"] + list(arrival_stations))
with col2:
    selected_destination = st.selectbox("Destination", options=["All"] + list(destination_stations))
with col3:
    selected_operator = st.selectbox("Operator", options=["All"] + list(operators))

filtered_data = draft_data.copy()
if selected_arrival != "All":
    filtered_data = filtered_data[draft_data["station_name"] == selected_arrival]

if selected_destination != "All":
    filtered_data = filtered_data[draft_data["destination_name"] == selected_destination]

if selected_operator != "All":
    filtered_data = filtered_data[draft_data["operator_name"] == selected_operator]

live_trains = filtered_data[[
    "service_uid",
    "station_name",
    "destination_name",
    "actual_arr_time",
    "actual_dep_time",
    "platform",
    "operator_name"
]]

live_trains.rename(columns={
    "service_uid": "Service ID",
    "station_name": "Arrival Station",
    "destination_name": "Destination",
    "actual_arr_time": "Arrival Time",
    "actual_dep_time": "Departure Time",
    "platform": "Platform",
    "operator_name": "Operator"
}, inplace=True)

st.dataframe(live_trains, hide_index=True, height=210)

if __name__ == '__main__':
    print(live_trains.head())