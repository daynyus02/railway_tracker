"""Contains the streamlit code to run the live dashboard."""
from os import environ as ENV
import datetime
from dotenv import load_dotenv
import streamlit as st
import psycopg2

from utils.live_data_visualisations import make_live_train_table, make_cancellations_pie, make_interruptions_bar
from utils.live_data_dataframes import fetch_data, filter_data, convert_times_to_datetime, add_status_column, add_delay_time, get_delays, get_cancelled_data, get_route_data, get_interruption_data

def get_connection():
    """Returns a psycopg2 connection to the RDS database."""
    connection = psycopg2.connect(host=ENV['DB_HOST'],
                            port=ENV['DB_PORT'],
                            dbname=ENV['DB_NAME'],
                            user=ENV['DB_USER'],
                            password=ENV['DB_PASSWORD'])
    return connection

if __name__ == '__main__':
    load_dotenv()
######### Dashboard Setup #########
    st.set_page_config(
    page_title="Railway Tracker",
    page_icon="🚆",
    layout="wide"
    )
    st.sidebar.image("your_logo.png", use_column_width=True)
    ### Fetching Data ###
    QUERY = """SELECT *
               FROM train_info_view 
               WHERE (service_date + scheduled_dep_time) >= (NOW() - INTERVAL '1 minute');"""
    conn = get_connection()
    data = fetch_data(QUERY, conn)
    if not data.empty:
        convert_times_to_datetime(data)
        add_status_column(data)

        st.title("🚆 Railway Tracker")

######### Filtering data based on user inputs #########
        arrival_stations = sorted(data["station_name"].unique())
        destination_stations = sorted(data["destination_name"].unique())
        operators = sorted(data["operator_name"].unique())
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_arrival = st.selectbox("Arrival", options=["All"] + list(arrival_stations))
        with col2:
            selected_destination = st.selectbox("Destination", options=["All"] + list(destination_stations))
        with col3:
            selected_operator = st.selectbox("Operator", options=["All"] + list(operators))
        filtered_data = filter_data(data, selected_arrival, selected_destination, selected_operator)

        selected_time_range = st.slider(
        "Filter Departure Time",
        min_value=datetime.time(0, 0),
        max_value=datetime.time(23, 59),
        value=(datetime.time(0, 0), datetime.time(23, 59)),
        format="HH:mm"
        )
        start, end = selected_time_range
        filtered_data = filtered_data[
        (filtered_data['scheduled_dep_time'].dt.time >= start) & (filtered_data['scheduled_dep_time'].dt.time <= end)]
        interruption_filter = st.sidebar.radio("Filter Interruption", ["All", "Delayed", "Cancelled"])
        if interruption_filter != "All":
            filtered_data = filtered_data[filtered_data['Status'] == interruption_filter]
######### Live train departure table #########
        styled_trains = make_live_train_table(filtered_data)
        st.subheader("Live Timetable 🚇:")
        st.dataframe(styled_trains, hide_index=True, height=210)
######### Summary Info #########
        st.markdown("### Summary Information 📊: ")
        delays = get_delays(data)
        filter_data(delays,selected_arrival, selected_destination, selected_operator)
        delays = add_delay_time(delays)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### Total departures: {filtered_data["service_uid"].nunique()}")
            if not delays.empty:
                st.markdown(f"#### Avg. Delay Time: {round(delays["delay_time"].mean())} minutes")
            else:
                st.markdown("#### Avg. Delay Time: 0")
        with col2:
            delay_number = delays["service_uid"].nunique()
            st.markdown(f"#### Delayed Stops: {delay_number}")
            st.markdown(f"#### Total Cancellations: {filtered_data[filtered_data["Status"] == "Cancelled"]["service_uid"].nunique()}")
######### Cancelled trains pie chart and interruptions bar chart #########
        cancelled = get_cancelled_data(data)
        cancelled_pie_chart = make_cancellations_pie(cancelled)
        interruptions = get_interruption_data(data)
        interruptions_chart = make_interruptions_bar(interruptions)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Total Cancellations per Operator: ")
            st.altair_chart(cancelled_pie_chart)
        with col2:
            st.markdown("### Interruptions per Operator:")
            st.altair_chart(interruptions_chart)
######### Routes table #########
        routes = get_route_data(delays)
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
    else:
        st.warning("No data available.")
