import streamlit as st
import sys
sys.path.append('..')

from database import display_connection_status

st.set_page_config(page_title="CalibViz Pipeline", layout="wide")

st.title("Calibration Visualizer")
st.write("Comparison of ABM3 model outputs and Household Travel Survey (HTS).")

st.header("📋 Table of Contents")

st.markdown("""


**Household Size Distribution** - household size distributions, capped at 5 (excluding group quarters)
          
**Vehicle Ownership** - vehicle ownership distributions for all vehicles

### Navigation

Use the sidebar to navigate between different pages of the application.
""")

st.divider()

st.info("👈 Select a page from the sidebar to get started")

# Display database connection status in the sidebar
display_connection_status()