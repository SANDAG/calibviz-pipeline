import sys

import streamlit as st

sys.path.append("..")

from database import display_connection_status, get_db_connection
from scenario_config import render_scenario_selector, format_scenario_sql_list

st.set_page_config(page_title="Overview", layout="wide")

st.title("Overview")

st.info(
    "Check the `include_gq` var in `dbt/dbt_project.yml` to see whether "
    "group quarters households/persons are included in these metrics."
)

display_connection_status()

# Get scenario selection
scenarios = render_scenario_selector()

# Query and display data
conn = get_db_connection()

scenarios_list = format_scenario_sql_list(scenarios)
df = conn.execute(f"""
    SELECT scenario, metric, ABM as abm, HTS as hts 
    FROM calibration_metrics.overview
    WHERE scenario IN ('{scenarios_list}')
""").fetch_df()

df["% Difference"] = ((df["abm"] - df["hts"]) / df["hts"] * 100).round(1)

df["hts"] = df["hts"].apply(lambda x: f"{int(x):,}")
df["abm"] = df["abm"].apply(lambda x: f"{int(x):,}")
df["% Difference"] = df["% Difference"].apply(lambda x: f"{x:.1f}%")

# Display data
table_col, separator_col, chart_col = st.columns([2, 0.1, 1])

with table_col:
    st.subheader("📊 Totals")
    st.dataframe(df, use_container_width=True, hide_index=True)
