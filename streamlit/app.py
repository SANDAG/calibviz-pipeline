import streamlit as st
import sys
sys.path.append('..')

from database import (
    get_db_connection,
    query_household_size,      # ← Shared query from database.py
    display_connection_status
)

st.set_page_config(page_title="CalibViz Pipeline", layout="wide")

st.title("CalibViz Pipeline")
st.write("This is the main application for the CalibViz data pipeline.")


# @st.cache_data  # Cache the query results
# def household_size(_conn: duckdb.DuckDBPyConnection):
#     start = time.time()
#     query = "SELECT hhsize, stg_percentage, hts_percentage FROM main.hhsize"
#     result = _conn.execute(query).fetch_df()
#     st.write(f"⏱️ Query time: {time.time() - start:.2f}s")
#     return result

# Query once and reuse the result
conn = get_db_connection()
df = query_household_size(conn)

# Display database connection status in the sidebar
display_connection_status()

st.dataframe(df)
st.bar_chart(df, x='hhsize', y=['abm_percentage', 'hts_percentage'], stack=False)