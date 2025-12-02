import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Trip Mode Distribution", layout="wide")

st.title("Trip Mode Comparison")

display_connection_status()

# Query and display data
conn = get_db_connection()
df = conn.execute("SELECT trip_mode, tour_mode, tour_purpose, abm_trips, hts_trips FROM calibration_metrics.trip_mode ORDER BY trip_mode").fetch_df()

# Prepare filter lists
trip_modes_list = sorted(df['trip_mode'].unique(), key=lambda x: int(x.split(':')[0]))
tour_modes_list = sorted(df['tour_mode'].unique(), key=lambda x: int(x.split(':')[0]))
tour_purposes_list = sorted(df['tour_purpose'].unique(), key=lambda x: int(x.split(':')[0]))

# Initialize selected lists
selected_trip_modes = []
selected_tour_modes = []
selected_purposes = []

# === FILTERS SECTION (Collapsible at top) ===
with st.expander("🔍 Filters", expanded=False):
    
    # Trip Mode Filter
    selected_trip_modes = st.multiselect(
        "Trip Mode",
        options=trip_modes_list,
        default=trip_modes_list
    )

    # Tour Mode Filter
    selected_tour_modes = st.multiselect(
        "Tour Mode",
        options=tour_modes_list,
        default=tour_modes_list
    )
    
    # Purpose Filter
    selected_purposes = st.multiselect(
        "Tour Purpose",
        options=tour_purposes_list,
        default=tour_purposes_list
    )

# Apply filters
df_filtered = df.copy()
if selected_trip_modes:
    df_filtered = df_filtered[df_filtered['trip_mode'].isin(selected_trip_modes)]
if selected_tour_modes:
    df_filtered = df_filtered[df_filtered['tour_mode'].isin(selected_tour_modes)]
if selected_purposes:
    df_filtered = df_filtered[df_filtered['tour_purpose'].isin(selected_purposes)]

df_filtered = df_filtered.groupby('trip_mode', as_index=False).agg({
    'abm_trips': 'sum',
    'hts_trips': 'sum'
})

# Calculate shares
total_abm = df_filtered['abm_trips'].sum()
total_hts = df_filtered['hts_trips'].sum()

df_filtered['abm_percentage'] = df_filtered['abm_trips'] * 100 / total_abm if total_abm > 0 else 0
df_filtered['hts_percentage'] = df_filtered['hts_trips'] * 100 / total_hts if total_hts > 0 else 0

# Keep only trip_mode and shares
df_filtered = df_filtered[['trip_mode', 'hts_percentage', 'abm_percentage']]

fig = go.Figure()

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_filtered['trip_mode'],
    y=df_filtered['hts_percentage'],
    hovertemplate='Trip Mode: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_filtered['trip_mode'],
    y=df_filtered['abm_percentage'],
    hovertemplate='Trip Mode: %{x}<br>ABM: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Trip Mode',
    yaxis_title='Percentage',
    xaxis_tickangle=45,
    yaxis_ticksuffix='%'
)

# === MAIN CONTENT: Chart and Table side by side ===
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")   
    
    st.dataframe(
        df_filtered,
        column_config={
            "abm_percentage": st.column_config.NumberColumn(
                "ABM Percentage",
                format="%.1f%%"
            ),
            "hts_percentage": st.column_config.NumberColumn(
                "HTS Percentage",
                format="%.1f%%"
            )
        },
        use_container_width=True,
        hide_index=True
    )

with separator_col:
    st.subheader("")  

with chart_col:
    st.subheader("📈 Distribution Comparison")
    st.plotly_chart(fig, use_container_width=True)