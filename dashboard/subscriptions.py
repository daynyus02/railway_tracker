# pylint: skip-file

# pylint: disable=invalid-name, non-ascii-file-name, import-error

"""A page allowing users to subscribe to services."""
from os import environ as ENV
import streamlit as st
import psycopg2
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

from utils.historical_data_dataframes import fetch_data, get_unique_routes, station_to_crs, get_unique_stations

load_dotenv()
conn = psycopg2.connect(host=ENV['DB_HOST'],
                            port=ENV['DB_PORT'],
                            dbname=ENV['DB_NAME'],
                            user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'])
data = fetch_data(conn)

""" Subscriptions """
email = st.text_input("Email address")
st.subheader("📲 Subscriptions: ")
with st.form("Subscriptions"):
    st.subheader("💥 Disruption Alerts:")
    unique_routes_list = get_unique_routes(data)
    route = st.selectbox("Please select a route: ", ["Choose a route."] + unique_routes_list)
    st.markdown("I want to recieve:")
    delay_information = st.checkbox("Delay Information - a notification each time a train is delayed on this route.")
    disruptions = st.checkbox("Disruptions - notifications when a new disruption affects this route.")

    submitted = st.form_submit_button("Submit")
    if submitted:
        try:
            if not email:
                st.error("Please enter your email at the top of this page.")
            if route == "Choose a route.":
                st.error("No route selected!")
            if not (delay_information or disruptions):
                st.error("Please select an option.")
            if email and (route != "Choose a route.") and (delay_information or disruptions):
                st.write("Thanks for subscribing!")
                sns_client = boto3.client('sns',
                                            region_name=ENV["REGION"],
                                            aws_access_key_id=ENV["ACCESS_KEY"],
                                            aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])
                stations = route.split(" to ")
                station1 = station_to_crs(stations[0])
                station2 = station_to_crs(stations[1])
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
        except ClientError:
            st.error("Invalid email address provided.")


with st.form("Reports:"):
    st.subheader("📊 Daily reports:")
    unique_stations_list = get_unique_stations(data)
    report_station = st.selectbox("Please select a station:", ["Choose a station."] + unique_stations_list)
    reports = st.checkbox("I would like to receive daily report summaries of services for this station.")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not email:
            st.error("Please enter your email at the top of this page.")
        if report_station == "Choose a route.":
            st.error("No station selected!")
        if not reports:
            st.error("Please confirm selection.")
        if email and (report_station != "Choose a route.") and reports:
            st.write("Thanks for subscribing!")
            sns_client = boto3.client('sns',
                                        region_name=ENV["REGION"],
                                        aws_access_key_id=ENV["ACCESS_KEY"],
                                        aws_secret_access_key=ENV["SECRET_ACCESS_KEY"])
            if reports:
                station = station_to_crs(report_station)
                topic_name = ENV["TOPIC_PREFIX"] + "reports-" + station
                topic = sns_client.create_topic(
                    Name= topic_name
                )
                response = sns_client.subscribe(
                TopicArn=topic.get("TopicArn"),
                Protocol='email',
                Endpoint=email,
                ReturnSubscriptionArn=True
            )

if __name__ == '__main__':
    pass
