import streamlit as st

st.title("Subscribe: ")
with st.form("subscriptions"):
    st.write("Pick a station:")
    st.checkbox("Great Western Railway")
    st.checkbox("Elizabeth line")
    st.write("Subscribe to a service:")
    email = st.text_input("Email address")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Thanks for submitting!")