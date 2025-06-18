"""Dashboard for historical data."""
from os import environ as ENV
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd
import boto3
import numpy as np


from utils.live_data_dataframes import convert_times_to_datetime, add_status_column, add_delay_time, get_delays, get_cancelled_data_per_operator
from utils.live_data_visualisations import make_operator_cancellations_pie
from utils.historical_data_visualisations import make_delays_heatmap, make_stations_cancellations_pie, make_cancellations_per_station_bar
from utils.historical_data_dataframes import get_unique_routes, get_cancellation_data_per_station, get_avg_delay_per_station

@st.cache_resource
def fetch_data(_connection)-> pd.DataFrame:
    query = """SELECT * 
               FROM train_info_view;"""
    data = pd.read_sql_query(query, _connection)
    _connection.close()
    return data

def station_to_crs(station_name: str) -> str:
    crs_codes = {
    "London Paddington": "PAD",
    "Bristol Temple Meads": "BRI",
    "Reading": "RDG",
    "Didcot Parkway": "DID",
    "Bath Spa": "BTH"
}
    return crs_codes.get(station_name)

st.set_page_config(
page_title="Historical Data",
page_icon="💾",
layout="wide"
)
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

######### Subscriptions #########
st.subheader("Subscriptions: ")
with st.form("subscriptions"):
    st.write("Please select a route: ")
    unique_routes_list = get_unique_routes(data)
    route = st.selectbox("Route", ["All"] + unique_routes_list)
    st.markdown("I want to recieve:")
    delay_information = st.checkbox("Delay Information - a notification each time a train is delayed on this route.")
    disruptions = st.checkbox("Disruptions - notifications when a new disruption affects this route.")
    reports = st.checkbox("Reports - daily report summaries of services on this route.")
    email = st.text_input("Email address")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Thanks for subscribing!")
        stations = route.split(" to ")
        station1 = station_to_crs(stations[0])
        station2 = station_to_crs(stations[1])
        sns_client = boto3.client('sns', 
                                    region_name=ENV["REGION"],
                                    aws_access_key_id=ENV["ACCESS_KEY"],
                                    aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])
        if reports:
            topic_name = ENV["TOPIC_PREFIX"] + "reports-" + f"{station1}-{station2}"
            topic = sns_client.create_topic(
                Name= topic_name
            )
            response = sns_client.subscribe(
            TopicArn=topic.get("TopicArn"),
            Protocol='email',
            Endpoint=email,
            ReturnSubscriptionArn=True
        )
        if delay_information:
            topic_name = ENV["TOPIC_PREFIX"] + "delays-" + f"{station1}-{station2}"
            topic = sns_client.create_topic(
                Name= topic_name
            )
            response = sns_client.subscribe(
            TopicArn=topic.get("TopicArn"),
            Protocol='email',
            Endpoint=email,
            ReturnSubscriptionArn=True
        )
        if disruptions:
            topic_name = ENV["TOPIC_PREFIX"] + "incidents-" + f"{station1}-{station2}"
            topic = sns_client.create_topic(
                Name= topic_name
            )
            response = sns_client.subscribe(
            TopicArn=topic.get("TopicArn"),
            Protocol='email',
            Endpoint=email,
            ReturnSubscriptionArn=True
        )
