from os import environ as ENV
import pandas as pd
import numpy as np
import datetime
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import altair as alt

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

def highlight_interruption(row):
    colours = [''] * len(row)
    if row.get('Status') == "Cancelled":
        colours = ['background-color: #3e0100'] * len(row)
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    elif row.get("Status") == "Delayed":
        colours[row.index.get_loc("Status")] = 'background-color: #FF6961'
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    else:
        colours[row.index.get_loc("Operator")] = highlight_operators(row)
    return colours

### Fetching Data ###
draft_data = pd.read_csv("trains.csv")
draft_data = draft_data.dropna(subset=["actual_arr_time"])
for col in ['actual_arr_time','scheduled_arr_time', 'actual_dep_time','scheduled_dep_time']:
    draft_data[col] = pd.to_datetime(draft_data[col], format='%H:%M:%S')


conditions = [(draft_data['cancelled'] == True),
              (draft_data['scheduled_dep_time'] < draft_data['actual_dep_time'])]
choices = ['Cancelled', 'Delayed']
draft_data['Status'] = np.select(conditions, choices, default="On Time")

### Dashboard Setup ###
st.title("🚆 Railway Tracker")

### Live trains table ###
arrival_stations = sorted(draft_data["station_name"].unique())
destination_stations = sorted(draft_data["destination_name"].unique())
operators = sorted(draft_data["operator_name"].unique())

filtered_data = draft_data.copy()

col1, col2, col3 = st.columns(3)
with col1:
    selected_arrival = st.selectbox("Arrival", options=["All"] + list(arrival_stations))
with col2:
    selected_destination = st.selectbox("Destination", options=["All"] + list(destination_stations))
with col3:
    selected_operator = st.selectbox("Operator", options=["All"] + list(operators))

if selected_arrival != "All":
    filtered_data = filtered_data[filtered_data["station_name"] == selected_arrival]

if selected_destination != "All":
    filtered_data = filtered_data[filtered_data["destination_name"] == selected_destination]

if selected_operator != "All":
    filtered_data = filtered_data[filtered_data["operator_name"] == selected_operator]

selected_time_range = st.slider(
    "Filter Departure Time",
    min_value=datetime.time(0, 0),
    max_value=datetime.time(23, 59),
    value=(datetime.time(0, 0), datetime.time(23, 59)),
    format="HH:mm"
)

start, end = selected_time_range
filtered_data = filtered_data[
    (filtered_data['scheduled_dep_time'].dt.time >= start) & (filtered_data['scheduled_dep_time'].dt.time <= end)
]

interruption_filter = st.sidebar.radio("Filter Interruption", ["All", "Delayed", "Cancelled"])
if interruption_filter != "All":
    filtered_data = filtered_data[filtered_data['Status'] == interruption_filter]

live_trains = filtered_data[[
    "service_uid",
    "station_name",
    "destination_name",
    "actual_arr_time",
    "actual_dep_time",
    "Status",
    "platform",
    "operator_name"
]]

live_trains.rename(columns={
    "service_uid": "Service ID",
    "station_name": "Arrival Station",
    "destination_name": "Destination",
    "platform": "Platform",
    "operator_name": "Operator"
}, inplace=True)

live_trains['Arrival Time'] = live_trains['actual_arr_time'].dt.time
live_trains['Departure Time'] = live_trains['actual_dep_time'].dt.time
live_trains = live_trains.drop(columns=["actual_dep_time", "actual_arr_time"])


live_trains = live_trains.sort_values(by='Departure Time')
styled_trains = live_trains.style.apply(highlight_interruption, axis=1)
st.subheader("Live Timetable 🚇:")
st.dataframe(styled_trains, hide_index=True, height=210)

st.markdown("### Summary Information 📊: ")
### Displaying delay info ###
delays = draft_data[["Status",
                     "service_uid",
                     "scheduled_dep_time",
                     "actual_dep_time", 
                     "station_name",
                     "origin_name",
                     "destination_name", 
                     "operator_name"
                     ]].copy()
delays = delays[delays["Status"] == "Delayed"]
if selected_arrival != "All":
    delays = delays[delays["station_name"] == selected_arrival]

if selected_destination != "All":
    delays = delays[delays["destination_name"] == selected_destination]

if selected_operator != "All":
    delays = delays[delays["operator_name"] == selected_operator]

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"#### Total departures: {filtered_data["service_uid"].nunique()}")

### Fetching average delay data ###
    delays["delay_time"] = delays["actual_dep_time"] - delays["scheduled_dep_time"]
    delays = delays[delays["delay_time"] > pd.Timedelta(0)]
    delays = delays.dropna(subset=["delay_time"])
    delays["delay_time"] = delays["delay_time"].dt.total_seconds() // 60

    if not delays.empty:
        st.markdown(f"#### Avg. Delay Time: {round(delays["delay_time"].mean())} minutes")
    else:
        st.markdown("#### Avg. Delay Time: 0")

    with col2:
        delay_number = delays["service_uid"].nunique()
        st.markdown(f"#### Delayed Stops: {delay_number}")
        st.markdown(f"#### Total Cancellations: {filtered_data[filtered_data["Status"] == "Cancelled"]["service_uid"].nunique()}")

### Pie chart of the total cancellations per operator ###

cancelled = draft_data[["service_uid","operator_name", "Status"]].copy()
cancelled = cancelled.groupby(["operator_name","Status"])["service_uid"].nunique().reset_index(name="Count").copy()
cancelled = cancelled[cancelled["Status"]=="Cancelled"].rename(columns={"operator_name": "Operator"})

operator_color_scale = alt.Scale(domain=['Great Western Railway', 
                                'Elizabeth line', 'CrossCountry'], range=['#0A493E','#6950a1', '#CA123F'])
cancellations_pie = alt.Chart(cancelled).mark_arc().encode(
    theta="Count",
    color=alt.Color("Operator", scale=operator_color_scale),
    tooltip=[alt.Tooltip("Operator"), alt.Tooltip("Count", title="Count")]
)

### Bar chart of the number of interruptions per operator ###
interruption_color_scale = alt.Scale(domain=['Cancelled','Delayed', 'On Time'], 
                                     range=['#f2f1ec', '#df543b', '#808080'])
interruptions = draft_data[["service_uid","operator_name", "Status"]].copy()
interruptions = interruptions.groupby(["operator_name", "Status"])["service_uid"].nunique().reset_index()
interruptions["percentage_of_trains"] = (interruptions["service_uid"]*100 / interruptions.groupby('operator_name')['service_uid'].transform('sum')).round(1)
interruptions_chart = alt.Chart(interruptions).mark_bar(size=30).encode(
    x=alt.X('Status:N', axis=None),
    y=alt.Y('percentage_of_trains', title="% of trains"),
    color=alt.Color('Status:N',scale=interruption_color_scale),
    column=alt.Column('operator_name:N', title='Operator'),
    tooltip=[alt.Tooltip('operator_name', title="Operator Name"),
             alt.Tooltip('Status'),
             alt.Tooltip('percentage_of_trains', title="% of trains")]
).properties(width=100)


col1, col2 = st.columns(2)
with col1:
    st.markdown("### Total Cancellations per Operator: ")
    st.altair_chart(cancellations_pie)
with col2:
    st.markdown("### Interruptions per Operator:")
    st.altair_chart(interruptions_chart)

### Table for the number of delays and average delay per route ###
routes = delays.groupby(["origin_name", "destination_name"]).agg(
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

col1,col2, col3 = st.columns([3,4,2])
with col1:
    st.markdown("### Most Delayed Routes:")
with col3:
    number_shown = st.radio('',["5", "10", "25", "50"], horizontal=True)
if number_shown == "5": 
    st.dataframe(routes.head(5), hide_index=True)
elif number_shown == "10": 
    st.dataframe(routes.head(10), hide_index=True)
elif number_shown == "25": 
    st.dataframe(routes.head(25), hide_index=True)
elif number_shown == "50": 
    st.dataframe(routes.head(50), hide_index=True)

if __name__ == '__main__':
    pass