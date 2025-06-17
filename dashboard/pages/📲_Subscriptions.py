import streamlit as st

st.title("Subscribe: ")
with st.form("subscriptions"):
    st.write("Please select a route: ")
    st.selectbox("Great Western Railway")
    st.selectbox("Elizabeth line")
    st.write("Subscribe to a service:")
    email = st.text_input("Email address")

    submitted = st.form_submit_button("Submit")
    if submitted:
        st.write("Thanks for submitting!")