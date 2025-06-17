"""Dashboard for historical data."""
from os import environ as ENV
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd
import boto3

from utils.live_data_dataframes import convert_times_to_datetime, add_status_column, add_delay_time, get_delays
from utils.historical_data_visualisations import make_delays_heatmap
from utils.historical_data_dataframes import get_unique_routes

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

if __name__ == '__main__':
    load_dotenv()
    conn = psycopg2.connect(host=ENV['DB_HOST'],
                                port=ENV['DB_PORT'],
                                dbname=ENV['DB_NAME'],
                                user=ENV['DB_USER'],
                                password=ENV['DB_PASSWORD'])
    data = fetch_data(conn)
    convert_times_to_datetime(data)
    add_status_column(data)

    delays=get_delays(data)
    delays = add_delay_time(delays)
    heatmap = make_delays_heatmap(delays)
    st.altair_chart(heatmap)

    st.subheader("Subscriptions: ")
    with st.form("subscriptions"):
        st.write("Please select a route: ")
        unique_routes_list = get_unique_routes(data)
        route = st.selectbox("Route", ["All"] + unique_routes_list)
        delay_information = st.checkbox("Delay Information")
        reports = st.checkbox("Reports")
        email = st.text_input("Email address")
        submitted = st.form_submit_button("Submit")
        if submitted:
            st.write("Thanks for subscribing!")
            stations = route.split(" to ")
            station1 = station_to_crs(stations[0])
            station2 = station_to_crs(stations[1])
            sns_client = boto3.client('sns', 
                                      region_name=ENV["AWS_REGION"],
                                      aws_access_key_id=ENV["AWS_ACCESS_KEY"],
                                      aws_secret_access_key=ENV["AWS_SECRET_ACCESS_KEY"])
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