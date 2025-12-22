import streamlit as st
import sys
sys.path.append('..')

from database import display_connection_status

pages = {
    "": [st.Page("pages/home_page.py", title="Home Page")],
    "Resident - Overall Metrics": [st.Page("pages/0_overview.py")],
    "Resident - Household Metrics": [st.Page("pages/resident/household_metrics/household_size.py"), 
                                     st.Page("pages/resident/household_metrics/vehicle_ownership.py")],
    "Resident - Ownership Subsidies Metrics": [st.Page("pages/resident/ownership_subsidies_metrics/transponder_ownership.py"), 
                                     st.Page("pages/resident/ownership_subsidies_metrics/transit_pass_ownership.py"),
                                     st.Page("pages/resident/ownership_subsidies_metrics/parking_subsidy.py"),
                                     st.Page("pages/resident/ownership_subsidies_metrics/transit_subsidy.py")],
    "Resident - Person Metrics": [st.Page("pages/resident/person_metrics/daily_activity_pattern.py")],
    "Resident - Work Location Metrics": [st.Page("pages/resident/work_metrics/work_from_home.py"), 
                                         st.Page("pages/resident/work_metrics/telecommute_frequency.py"),
                                         st.Page("pages/resident/work_metrics/district_flows.py"), 
                                         st.Page("pages/resident/work_metrics/external_location.py")],
    "Resident - Trip Metrics": [st.Page("pages/resident/trip_metrics/tour_mode.py"),
                                st.Page("pages/resident/trip_metrics/trip_mode.py")],
    "Airport Metrics": [st.Page("pages/airport/airport_tour_mode.py")]
}

pg = st.navigation(pages)

pg.run()
