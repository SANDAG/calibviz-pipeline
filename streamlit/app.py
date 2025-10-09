import streamlit as st
import duckdb

st.title("CalibViz Pipeline")
st.write("This is the main application for the CalibViz data pipeline.")

@st.cache_resource
def get_db_connection():
    conn = duckdb.connect('../files.duckdb')
    return conn

@st.cache_data  # Cache the query results
def household_size(_conn: duckdb.DuckDBPyConnection):
    query = "SELECT * FROM main.hhsize"
    result = _conn.execute(query)
    return result.df()

# Query once and reuse the result
conn = get_db_connection()
df = household_size(conn)

st.table(df)
st.bar_chart(df, x='hhsize', y=['stg_percentage', 'hts_percentage'], stack=False)