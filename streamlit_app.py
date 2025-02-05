import streamlit as st
from langgraph_agent import langgraph_agent
import datetime


st.title("Google Calendar Booking Agent")

event_date = st.date_input("Select date for the appointment")
event_start_time  = st.time_input("Select start time for the appointment")
event_end_time = st.time_input("Select end time for the appointment")


if event_date and event_start_time and event_start_time:
    start_datetime = datetime.datetime.combine(event_date, event_start_time)
    end_datetime = datetime.datetime.combine(event_date, event_end_time)


    user_request = f"Book an Appointment on {start_datetime.isoformat} to {end_datetime.isoformat}"


    if st.button("Book Appointment"):
        try:
            result = langgraph_agent.run(user_request)
            st.write("Agent Response: ", result)
        except Exception as e:
            st.error(f"An Error occurred: {e}")
else:
    st.warning("Please select the appointment date and time")