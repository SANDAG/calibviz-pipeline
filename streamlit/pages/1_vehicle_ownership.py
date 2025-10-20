import streamlit as st
import sys
sys.path.append('..')

from database import (
    get_db_connection,
    query_household_size,      # ← Shared query from database.py
    display_connection_status
)

st.title("Vehicle Ownership Analysis")

# Display database connection status in the sidebar
display_connection_status()

conn = get_db_connection()

df = conn.execute("SELECT * FROM main.auto_ownership").fetch_df()

st.dataframe(df)
st.bar_chart(df, x='auto_ownership', y=['abm_percentage', 'hts_percentage'], stack=False)