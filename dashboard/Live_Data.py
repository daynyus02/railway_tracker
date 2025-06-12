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

draft_data = pd.read_csv("trains.csv")
draft_data = draft_data.dropna(subset=["actual_arr_time"])
for col in ['actual_arr_time', 'actual_dep_time', 'scheduled_arr_time', 'scheduled_dep_time']:
    draft_data[col] = pd.to_datetime(draft_data[col], format='%H:%M:%S').dt.time

st.title("Railway Tracker 🚆")

def highlight_operators(row):
    colors = [''] * len(row)
    operator = row["Operator"]
    if operator == "Elizabeth line":
        colors[row.index.get_loc("Operator")] = 'background-color: #CBC3E3'
    elif operator == "CrossCountry":
        colors[row.index.get_loc("Operator")] = 'background-color: #A24857'
    elif operator == "Great Western Railway":
        colors[row.index.get_loc("Operator")] = 'background-color: #2E6F40'
    return colors

def highlight_delays(row):
    colors = [''] * len(row)
    arrival = row["Arrival Time"]
    scheduled = row["scheduled_arr_time"]
    if pd.isnull(arrival) or pd.isnull(scheduled):
        return colors
    delayed = arrival > scheduled
    if delayed:
        colors[row.index.get_loc("Arrival Time")] = 'background-color: #FF6961'
    return colors

### Live trains table ###
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
    "scheduled_arr_time",
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

styled_trains = live_trains.style.apply(highlight_delays, axis=1).apply(highlight_operators, axis=1)
st.dataframe(styled_trains, hide_index=True, height=210)

### Live delay table ###
delays = draft_data[draft_data["actual_arr_time"] > draft_data["scheduled_arr_time"]]
filtered_delays = delays.copy()
if selected_arrival != "All":
    filtered_delays = filtered_delays[draft_data["station_name"] == selected_arrival]

if selected_destination != "All":
    filtered_delays = filtered_delays[draft_data["destination_name"] == selected_destination]

if selected_operator != "All":
    filtered_delays = filtered_delays[draft_data["operator_name"] == selected_operator]

live_delays = filtered_delays[[
    "service_uid",
    "station_name",
    "destination_name",
    "scheduled_arr_time",
    "actual_arr_time",
    "actual_dep_time",
    "platform",
    "operator_name"
]]

live_delays.rename(columns={
    "service_uid": "Service ID",
    "station_name": "Arrival Station",
    "destination_name": "Destination",
    "actual_arr_time": "Arrival Time",
    "actual_dep_time": "Departure Time",
    "platform": "Platform",
    "operator_name": "Operator"
}, inplace=True)
styled_delays = live_delays.style.apply(highlight_operators, axis=1).apply(highlight_delays, axis=1)
st.dataframe(styled_delays, hide_index=True, height=210)

### Live cancellations data ###

if __name__ == '__main__':
    for col in ['actual_arr_time', 'actual_dep_time', 'scheduled_arr_time', 'scheduled_dep_time']:
        draft_data[col] = pd.to_datetime(draft_data[col], format='%H:%M:%S').dt.time
    print(draft_data.dtypes)