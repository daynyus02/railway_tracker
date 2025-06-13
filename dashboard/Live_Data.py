from os import environ as ENV
import pandas as pd
import numpy as np
import datetime
from dotenv import load_dotenv
import streamlit as st
import psycopg2

# conn = psycopg2.connect(host=ENV['DB_HOST'],
#                         port=ENV['DB_PORT'],
#                         dbname=ENV['DB_NAME'],
#                         user=ENV['DB_USER'],
#                         password=ENV['DB_PASSWORD'])

# st.set_page_config(
#     page_title="Railway Tracker",
#     page_icon="🚆",
#     layout="wide"
# )

### Table Highlighting ###
def highlight_operators(row):
    operator = row.get("Operator")
    operator_colours = {"Elizabeth line": 'background-color: #6950a1',
                       "CrossCountry": 'background-color: #CA123F',
                       "Great Western Railway": 'background-color: #0A493E'
                       }
    if operator in operator_colours:
        return operator_colours[operator]
    return ''

def highlight_interruptions(row):
    colours = [''] * len(row)
    if row.get('Interruptions') == "Cancelled":
        colours = ['background-color: #3e0100'] * len(row)
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    elif row.get("Interruptions") == "Delayed":
        colours[row.index.get_loc("Interruptions")] = 'background-color: #FF6961'
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    else:
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    return colours

### Fetching Data ###
draft_data = pd.read_csv("trains.csv")
draft_data = draft_data.dropna(subset=["actual_arr_time"])
for col in ['actual_arr_time', 'actual_dep_time', 'scheduled_arr_time', 'scheduled_dep_time']:
    draft_data[col] = pd.to_datetime(draft_data[col], format='%H:%M:%S').dt.time

conditions = [(draft_data['cancelled'] == True),
              (draft_data['scheduled_arr_time'] < draft_data['actual_arr_time'])]
choices = ['Cancelled', 'Delayed']
draft_data['Interruptions'] = np.select(conditions, choices, default=None)

### Dashboard Setup ###
st.title("Railway Tracker 🚆")

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

selected_time_range = st.slider(
    "Filter Departure Time",
    min_value=datetime.time(0, 0),
    max_value=datetime.time(23, 59),
    value=(datetime.time(0, 0), datetime.time(23, 59)),
    format="HH:mm"
)

start, end = selected_time_range
filtered_data = filtered_data[
    (filtered_data['scheduled_dep_time'] >= start) & (filtered_data['scheduled_dep_time'] <= end)
]

live_trains = filtered_data[[
    "service_uid",
    "station_name",
    "destination_name",
    "actual_arr_time",
    "actual_dep_time",
    "Interruptions",
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

live_trains = live_trains.sort_values(by='Departure Time')
styled_trains = live_trains.style.apply(highlight_interruptions, axis=1)
st.subheader("Live Timetable:")
st.dataframe(styled_trains, hide_index=True, height=210)

### Displaying delay info ###
delays = draft_data[["Interruptions",
                     "service_uid",
                     "scheduled_arr_time",
                     "actual_arr_time", 
                     "station_name", 
                     "destination_name",
                     "operator_name"
                     ]].copy()
if selected_arrival != "All":
    delays = delays[delays["station_name"] == selected_arrival]

if selected_destination != "All":
    delays = delays[delays["destination_name"] == selected_destination]

if selected_operator != "All":
    delays = delays[delays["operator_name"] == selected_operator]

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### Total departures: {delays["service_uid"].nunique()}")

with col2:
    delay_number = delays[delays["Interruptions"] == "Delayed"]["service_uid"].nunique()
    st.markdown(f"### Total Delays: {delay_number}")

### Fetching average delay data ###
delays['scheduled_arr_time'] = pd.to_datetime(delays['scheduled_arr_time'], format='%H:%M:%S')
delays['actual_arr_time'] = pd.to_datetime(delays['actual_arr_time'], format='%H:%M:%S')
delays["delay_time"] = delays["actual_arr_time"] - delays["scheduled_arr_time"]
delays = delays[delays["delay_time"] > pd.Timedelta(0)]
delays["delay_time"] = delays["delay_time"].dt.total_seconds() // 60
delays["delay_time"] = delays["delay_time"].fillna(0).astype(int)

if not delays.empty:
    st.markdown(f"### Average Delay Time: {round(delays["delay_time"].mean())} minutes")
else:
    st.markdown("### Average Delay Time: 0")





if __name__ == '__main__':
    print(delays)