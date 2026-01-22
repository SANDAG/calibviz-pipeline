import sys

import streamlit as st

sys.path.append("..")

from database import display_connection_status, get_db_connection

st.set_page_config(page_title="Overview", layout="wide")

st.title("Overview")

display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute(
    "SELECT metric, ABM as abm, HTS as hts FROM calibration_metrics.overview"
).fetch_df()

df["% Difference"] = ((df["abm"] - df["hts"]) / df["hts"] * 100).round(1)

df["hts"] = df["hts"].apply(lambda x: f"{int(x):,}")
df["abm"] = df["abm"].apply(lambda x: f"{int(x):,}")
df["% Difference"] = df["% Difference"].apply(lambda x: f"{x:.1f}%")

# Display data
table_col, separator_col, chart_col = st.columns([2, 0.1, 1])

with table_col:
    st.subheader("📊 Totals")
    st.dataframe(df, use_container_width=True, hide_index=True)
