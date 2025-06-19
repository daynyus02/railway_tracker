import streamlit as st

live_data = st.Page("live_data.py", title="Live Data", icon="📈")
historical_data = st.Page("historical_data.py", title="Historical Data", icon="💾")
subscriptions = st.Page("subscriptions.py", title="Subscriptions", icon="📲")
reports = st.Page("reports.py", title="Download Reports", icon="📂")

pg = st.navigation([live_data, historical_data, subscriptions, reports])
st.set_page_config(
page_title="Railway Tracker",
page_icon="🚆",
layout="wide"
)
pg.run()