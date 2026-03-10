import sys

import plotly.graph_objects as go

import streamlit as st

sys.path.append("..")

from database import display_connection_status, get_db_connection

st.set_page_config(page_title="Trip Mode Distribution", layout="wide")

st.title("Trip Mode Comparison")

display_connection_status()

# Query and display data
conn = get_db_connection()
df = conn.execute(
    "SELECT trip_mode, tour_mode, tour_purpose, abm_trips, survey_trips FROM calibration_metrics.trip_mode WHERE tour_purpose != 'total' and tour_mode NOT IN ('TOTAL') ORDER BY trip_mode"
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

df_filtered = df_filtered.groupby("trip_mode", as_index=False).agg(
    {"abm_trips": "sum", "survey_trips": "sum"}
)

# Calculate shares
total_abm = df_filtered["abm_trips"].sum()
total_survey = df_filtered["survey_trips"].sum()

df_filtered["abm_percentage"] = (
    df_filtered["abm_trips"] * 100 / total_abm if total_abm > 0 else 0
)
df_filtered["survey_percentage"] = (
    df_filtered["survey_trips"] * 100 / total_survey if total_survey > 0 else 0
)

# Keep only trip_mode and shares
df_filtered = df_filtered[["trip_mode", "survey_percentage", "abm_percentage"]]

fig = go.Figure()

# Add Survey bars
fig.add_trace(
    go.Bar(
        name="Survey",
        x=df_filtered["trip_mode"],
        y=df_filtered["survey_percentage"],
        hovertemplate="Trip Mode: %{x}<br>Survey: %{y:.1f}%<extra></extra>",
    )
)

# Add ABM bars
fig.add_trace(
    go.Bar(
        name="ABM",
        x=df_filtered["trip_mode"],
        y=df_filtered["abm_percentage"],
        hovertemplate="Trip Mode: %{x}<br>ABM: %{y:.1f}%<extra></extra>",
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

    st.dataframe(
        df_filtered,
        column_config={
            "abm_percentage": st.column_config.NumberColumn(
                "ABM Percentage", format="%.1f%%"
            ),
            "survey_percentage": st.column_config.NumberColumn(
                "Survey Percentage", format="%.1f%%"
            ),
        },
        use_container_width=True,
        hide_index=True,
    )

with separator_col:
    st.subheader("")

with chart_col:
    st.subheader("📈 Distribution Comparison")
    st.plotly_chart(fig, use_container_width=True)
