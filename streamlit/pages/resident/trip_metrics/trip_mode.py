import sys

import plotly.graph_objects as go

import streamlit as st

sys.path.append("..")

from database import display_connection_status, get_db_connection
from scenario_config import render_scenario_selector, format_scenario_sql_list

st.set_page_config(page_title="Trip Mode Distribution", layout="wide")

st.title("Trip Mode Comparison")

display_connection_status()

# Get scenario selection
scenarios = render_scenario_selector()

# Query and display data
conn = get_db_connection()
scenarios_list = format_scenario_sql_list(scenarios)
df = conn.execute(
    f"SELECT scenario, trip_mode, tour_mode, tour_purpose, abm_trips, survey_trips FROM calibration_metrics.trip_mode WHERE scenario IN ('{scenarios_list}') and tour_purpose != 'total' and tour_mode NOT IN ('TOTAL') ORDER BY trip_mode"
).fetch_df()

st.dataframe(df)

# Prepare filter lists
trip_modes_list = sorted(df["trip_mode"].unique(), key=lambda x: int(x.split(":")[0]))
tour_modes_list = sorted(df["tour_mode"].unique(), key=lambda x: int(x.split(":")[0]))
tour_purposes_list = sorted(
    df["tour_purpose"].unique(), key=lambda x: int(x.split(":")[0])
)

# Initialize selected lists
selected_trip_modes = []
selected_tour_modes = []
selected_tour_purposes = []

# Initialize checkboxes in session state
if "trip_mode_initialized" not in st.session_state:
    st.session_state.trip_mode_initialized = True
    for mode in tour_modes_list:
        st.session_state[f"m_{mode}"] = True
    for trip_mode in trip_modes_list:
        st.session_state[f"t_{trip_mode}"] = True
    for purp in tour_purposes_list:
        st.session_state[f"p_{purp}"] = True

# === FILTERS SECTION (Collapsible at top) ===
with st.expander("🔍 Filters", expanded=False):
    if st.button("🔄 Reset Filters", use_container_width=False):
        for mode in tour_modes_list:
            st.session_state[f"m_{mode}"] = True

        for trip_mode in trip_modes_list:
            st.session_state[f"t_{trip_mode}"] = True

        for purp in tour_purposes_list:
            st.session_state[f"p_{purp}"] = True

        st.rerun()

    st.divider()

    filter_cols = st.columns(3)

    # Tour Mode Filter
    with filter_cols[0]:
        st.markdown("**Tour Mode**")
        for mode in tour_modes_list:
            if st.checkbox(mode, key=f"m_{mode}"):
                selected_tour_modes.append(mode)

    # Trip Mode Filter
    with filter_cols[1]:
        st.markdown("**Trip Mode**")
        for trip_mode in trip_modes_list:
            if st.checkbox(trip_mode, key=f"t_{trip_mode}"):
                selected_trip_modes.append(trip_mode)

    # Purpose Filter
    with filter_cols[2]:
        st.markdown("**Tour Purpose**")
        for purp in tour_purposes_list:
            if st.checkbox(purp, key=f"p_{purp}"):
                selected_tour_purposes.append(purp)

# Apply filters
df_filtered = df.copy()
if selected_trip_modes:
    df_filtered = df_filtered[df_filtered["trip_mode"].isin(selected_trip_modes)]
if selected_tour_modes:
    df_filtered = df_filtered[df_filtered["tour_mode"].isin(selected_tour_modes)]
if selected_tour_purposes:
    df_filtered = df_filtered[df_filtered["tour_purpose"].isin(selected_tour_purposes)]

# Aggregate by scenario and trip_mode
df_filtered = df_filtered.groupby(["scenario", "trip_mode"], as_index=False).agg(
    {"abm_trips": "sum", "survey_trips": "sum"}
)

# Calculate shares per scenario
df_filtered["abm_percentage"] = 0
df_filtered["survey_percentage"] = 0

for scenario in scenarios:
    scenario_mask = df_filtered["scenario"] == scenario
    total_abm = df_filtered.loc[scenario_mask, "abm_trips"].sum()
    total_survey = df_filtered.loc[scenario_mask, "survey_trips"].sum()
    
    if total_abm > 0:
        df_filtered.loc[scenario_mask, "abm_percentage"] = (
            df_filtered.loc[scenario_mask, "abm_trips"] * 100 / total_abm
        )
    if total_survey > 0:
        df_filtered.loc[scenario_mask, "survey_percentage"] = (
            df_filtered.loc[scenario_mask, "survey_trips"] * 100 / total_survey
        )

# Pivot for display
df_pivot_abm = df_filtered.pivot_table(
    index="trip_mode",
    columns="scenario",
    values="abm_percentage",
    aggfunc="first"
).reset_index()

# Get survey data (same across scenarios)
df_survey = df_filtered.groupby("trip_mode").agg({
    "survey_percentage": "first"
}).reset_index()

# Merge
df_display = df_pivot_abm.merge(df_survey, on="trip_mode", how="left")

fig = go.Figure()

# Add Survey bars
fig.add_trace(
    go.Bar(
        name="Survey",
        x=df_display["trip_mode"],
        y=df_display["survey_percentage"],
        hovertemplate="Trip Mode: %{x}<br>Survey: %{y:.1f}%<extra></extra>",
    )
)

# Add ABM bars for each scenario
for scenario in scenarios:
    if scenario in df_display.columns:
        fig.add_trace(
            go.Bar(
                name=f"ABM ({scenario})",
                x=df_display["trip_mode"],
                y=df_display[scenario],
                hovertemplate=f"Trip Mode: %{{x}}<br>ABM ({scenario}): %{{y:.1f}}%<extra></extra>",
            )
        )

fig.update_layout(
    barmode="group",
    xaxis_title="Trip Mode",
    yaxis_title="Percentage",
    xaxis_tickangle=45,
    yaxis_ticksuffix="%",
)

# === MAIN CONTENT: Chart and Table side by side ===
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    
    # Build column config dynamically
    column_config = {
        "survey_percentage": st.column_config.NumberColumn(
            "Survey Percentage", format="%.1f%%"
        )
    }
    for scenario in scenarios:
        if scenario in df_display.columns:
            column_config[scenario] = st.column_config.NumberColumn(
                f"ABM {scenario} %", format="%.1f%%"
            )

    st.dataframe(
        df_display,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
    )

with separator_col:
    st.subheader("")

with chart_col:
    st.subheader("📈 Distribution Comparison")
    st.plotly_chart(fig, use_container_width=True)
