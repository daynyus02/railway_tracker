"""Contains the streamlit code to run the live dashboard."""
from os import environ as ENV
import datetime
from dotenv import load_dotenv
import streamlit as st

from utils.live_data_visualisations import make_interruptions_bar, make_live_train_table
from utils.live_data_dataframes import fetch_data, filter_data, convert_times_to_datetime, add_status_column, add_delay_time, get_delays, get_route_data, get_interruption_data, get_connection

if __name__ == '__main__':
    load_dotenv()
    QUERY = """SELECT *
               FROM train_info_view 
               WHERE (service_date + scheduled_dep_time) >= (NOW() - INTERVAL '1 minute');"""
    conn = get_connection()
    data = fetch_data(QUERY, conn)
    if not data.empty:
        convert_times_to_datetime(data)
        add_status_column(data)

        st.title("🚆 Railway Tracker")

        arrival_stations = sorted(data["station_name"].unique())
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_arrival = st.selectbox("Current Station", options=["All"] + arrival_stations)
        with col2:
            if selected_arrival != "All":
                destination_subset = data[data["station_name"] == selected_arrival]
            else:
                destination_subset = data
            destination_stations = sorted(destination_subset["destination_name"].unique())
            selected_destination = st.selectbox("Destination", options=["All"] + destination_stations)
        with col3:
            if selected_arrival != "All" and selected_destination != "All":
                operator_subset = data[(data["station_name"] == selected_arrival)&(data["destination_name"] == selected_destination)]
            elif selected_arrival != "All":
                operator_subset = data[data["station_name"] == selected_arrival]
            elif selected_destination != "All":
                operator_subset = data[data["destination_name"] == selected_destination]
            else:
                operator_subset = data
            operators = sorted(operator_subset["operator_name"].unique())
            selected_operator = st.selectbox("Operator", options=["All"] + operators)
        filtered_data = filter_data(data, selected_arrival, selected_destination, selected_operator)

        selected_time_range = st.slider(
        "**Filter Departure Time:**",
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

        if interruption_filter == "Cancelled":
            styled_arrivals = make_live_train_table(filtered_data, True, 'arrival')
        else:
            styled_arrivals = make_live_train_table(filtered_data, False, 'arrival')
        st.subheader("Live Arrivals 🚇:")
        st.dataframe(styled_arrivals, hide_index=True, height=210)

        if interruption_filter == "Cancelled":
            styled_departures = make_live_train_table(filtered_data, True, 'departure')
        else:
            styled_departures = make_live_train_table(filtered_data, False, 'departure')
        st.subheader("Live Departures 🚇:")
        st.dataframe(styled_departures, hide_index=True, height=210)

        all_delays = get_delays(data)
        all_delays = add_delay_time(all_delays)
        routes = get_route_data(all_delays)
        col1,col2, col3 = st.columns([3,4,2])
        with col1:
            st.markdown("### Most Delayed Routes:")
        with col3:
            number_shown = st.radio('Show',["5", "10", "25"], horizontal=True, label_visibility='hidden')
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

        st.markdown("### Summary Information 📊: ")
        delays = get_delays(data)
        delays = filter_data(delays, selected_arrival, selected_destination, selected_operator)
        delays = add_delay_time(delays)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### Total Tracked Services: {filtered_data["service_uid"].nunique()}")
            if not delays.empty:
                st.markdown(f"#### Avg. Delay Time: {round(delays["delay_time"].mean())} minutes")
            else:
                st.markdown("#### Avg. Delay Time: 0")
        with col2:
            delay_number = delays["service_uid"].nunique()
            st.markdown(f"#### Delayed Stops: {delay_number}")
            st.markdown(f"#### Total Cancellations: {filtered_data[filtered_data["Status"] == "Cancelled"]["service_uid"].nunique()}")

        interruptions = get_interruption_data(data)
        interruptions_chart = make_interruptions_bar(interruptions)
        st.markdown("### Interruptions per Operator:")
        st.altair_chart(interruptions_chart, use_container_width=True)

if __name__ == '__main__':
    pass
