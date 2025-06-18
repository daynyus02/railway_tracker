from os import environ as ENV
import streamlit as st
import psycopg2
from dotenv import load_dotenv
import boto3

from utils.historical_data_dataframes import fetch_data, get_unique_routes, station_to_crs

load_dotenv()
conn = psycopg2.connect(host=ENV['DB_HOST'],
                            port=ENV['DB_PORT'],
                            dbname=ENV['DB_NAME'],
                            user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'])
data = fetch_data(conn)

######### Subscriptions #########
st.subheader("📲 Subscriptions: ")
with st.form("subscriptions"):
    st.write("Please select a route: ")
    unique_routes_list = get_unique_routes(data)
    route = st.selectbox("Route", ["Choose a route."] + unique_routes_list)
    st.markdown("I want to recieve:")
    delay_information = st.checkbox("Delay Information - a notification each time a train is delayed on this route.")
    disruptions = st.checkbox("Disruptions - notifications when a new disruption affects this route.")
    reports = st.checkbox("Reports - daily report summaries of services on this route.")
    email = st.text_input("Email address")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if route == "Choose a route.":
            st.error("No route selected!")
        else:
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



