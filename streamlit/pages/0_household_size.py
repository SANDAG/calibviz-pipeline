import streamlit as st
import sys
sys.path.append('..')

from database import (
    get_db_connection,
    query_household_size,
    display_connection_status
)

st.set_page_config(page_title="Household Size Distribution", layout="wide")

st.title("Household Size Distribution")


display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT hhsize, abm_percentage, hts_percentage FROM main.hhsize").fetch_df()


# Display data
st.subheader("📊 Data Table")
st.dataframe(df, use_container_width=True)

st.divider()

# Display chart
st.subheader("📈 Distribution Comparison")
st.bar_chart(df, x='hhsize', y=['abm_percentage', 'hts_percentage'], stack=False)