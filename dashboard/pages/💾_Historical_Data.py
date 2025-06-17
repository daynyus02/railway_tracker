"""Dashboard for historical data."""
from os import environ as ENV
from dotenv import load_dotenv
import streamlit as st
import psycopg2
import pandas as pd


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
    st.selectbox("Route", ["All"] + unique_routes_list)
    delay_information = st.checkbox("Delay Information")
    distruption = st.checkbox("Disruption")
    email = st.text_input("Email address")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Thanks for submitting!")

