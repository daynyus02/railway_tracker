# pylint: skip-file
# pylint: disable=invalid-name, non-ascii-file-name, import-error, F0001
"""Dashboard for historical data."""
from os import environ as ENV
from dotenv import load_dotenv
import streamlit as st
import psycopg2


from utils.live_data_dataframes import convert_times_to_datetime, add_status_column, add_delay_time, get_delays, get_cancelled_data_per_operator
from utils.live_data_visualisations import make_operator_cancellations_pie
from utils.historical_data_visualisations import make_delays_heatmap, make_stations_cancellations_pie, make_cancellations_per_station_bar
from utils.historical_data_dataframes import get_cancellation_data_per_station, get_avg_delay_per_station,fetch_data


st.logo("logo.png", size='large')
st.title("💾 Historical Data:")
window_filter = st.radio("Filter Date Window:", ["On", "Before", "After"], horizontal=True)
filter_date = st.date_input(label="Show data after:")
load_dotenv()
conn = psycopg2.connect(host=ENV['DB_HOST'],
                            port=ENV['DB_PORT'],
                            dbname=ENV['DB_NAME'],
                            user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'])
data = fetch_data(conn)
convert_times_to_datetime(data)
add_status_column(data)

if window_filter == "On":
    data = data[data["service_date"] == filter_date]
elif window_filter == "Before":
    data = data[data["service_date"] < filter_date]
elif window_filter == "After":
    data = data[data["service_date"] > filter_date]

delays=get_delays(data)
delays = add_delay_time(delays)

######### Heatmap of delays over time #########
heatmap = make_delays_heatmap(delays)
st.subheader("Delay peak times:")
if data.empty:
    st.warning("No Data.")
else:
    st.altair_chart(heatmap)
######### Cancellations pie charts #########
col1,col2 = st.columns(2)
with col1:
    operator_cancellations = get_cancelled_data_per_operator(data)
    operator_cancellations_pie = make_operator_cancellations_pie(operator_cancellations)
    st.subheader("Cancellations per Operator:")
    st.altair_chart(operator_cancellations_pie)
with col2:
    station_cancellations = get_cancellation_data_per_station(data)
    station_cancellations_pie = make_stations_cancellations_pie(station_cancellations)
    st.subheader("Cancellations per station:")
    st.altair_chart(station_cancellations_pie)

######### Cancellations per station bar #########
delays_per_station = get_delays(data)
delays_per_station = add_delay_time(delays_per_station)
delays_per_station = get_avg_delay_per_station(delays_per_station)
delays_per_station_bar = make_cancellations_per_station_bar(delays_per_station)
st.subheader("Average delay per station: ")
st.altair_chart(delays_per_station_bar)
