import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)


st.set_page_config(page_title="Overview", layout="wide")

st.title("Overview")

display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT Variables, HTS, ABM FROM calibration_metrics.overview").fetch_df()

df['% Difference'] = ((df['ABM'] - df['HTS']) / df['HTS'] * 100).round(1)

df['HTS'] = df['HTS'].apply(lambda x: f"{int(x):,}")
df['ABM'] = df['ABM'].apply(lambda x: f"{int(x):,}")
df['% Difference'] = df['% Difference'].apply(lambda x: f"{x:.1f}%")

df_display = df.copy()

# Display data
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Totals")
    st.dataframe(
        df_display,
        use_container_width=True,
        hide_index=True
    )