import streamlit as st
import sys
sys.path.append('..')

from database import display_connection_status

pages = {
    "": [st.Page("pages/home_page.py", title="Home Page")],
    "Resident - Household Metrics": [st.Page("pages/resident/household_metrics/1_household_size.py"), 
                                     st.Page("pages/resident/household_metrics/2_vehicle_ownership.py"),
                                     st.Page("pages/resident/household_metrics/3_transponder_ownership.py")],
    "Resident - Person Metrics": [],
    "Resident - Trip Metrics": [st.Page("pages/resident/trip_metrics/4_tour_mode.py"),
                                st.Page("pages/resident/trip_metrics/5_trip_mode.py")],
    "Airport Metrics": [st.Page("pages/airport/5_airport_tour_mode.py")]
}

pg = st.navigation(pages)

pg.run()
