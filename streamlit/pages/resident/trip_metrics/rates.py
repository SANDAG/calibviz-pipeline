"""
Trip and Tour Rates Visualization

This page displays aggregate trip and tour rate metrics comparing ABM model outputs 
with HTS survey data. Metrics include:
- Trips per Household
- Trips per Person  
- Tours per Person
- Stops per Person
"""

import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)
from scenario_config import (
    render_scenario_selector,
    format_scenario_sql_list
)

st.set_page_config(page_title="Trip and Tour Rates", layout="wide")

st.title("Trip and Tour Rates")

display_connection_status()

# Get scenario selection
scenarios = render_scenario_selector()

# Query metrics data from database
conn = get_db_connection()

scenarios_list = format_scenario_sql_list(scenarios)
df = conn.execute(f"""
    SELECT scenario, metric, hts_value, abm_value 
    FROM calibration_metrics.trip_tour_rates
    WHERE scenario IN ('{scenarios_list}')
""").fetch_df()

# Pivot ABM data by scenario
df_pivot_abm = df.pivot_table(
    index='metric',
    columns='scenario',
    values='abm_value',
    aggfunc='first'
).reset_index()

# Get HTS data (same across scenarios)
df_hts = df.groupby('metric').agg({
    'hts_value': 'first'
}).reset_index()

# Merge ABM and HTS data
df_display = df_pivot_abm.merge(df_hts, on='metric', how='left')

# Create grouped bar chart
fig = go.Figure()

# Add HTS bars (survey data)
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['metric'],
    y=df_display['hts_value'],
    text=df_display['hts_value'].round(2),
    textposition='outside',
    hovertemplate='%{x}<br>HTS: %{y:.2f}<extra></extra>'
))

# Add ABM bars for each scenario
for scenario in scenarios:
    if scenario in df_display.columns:
        fig.add_trace(go.Bar(
            name=f'ABM ({scenario})',
            x=df_display['metric'],
            y=df_display[scenario],
            text=df_display[scenario].round(2),
            textposition='outside',
            hovertemplate=f'%{{x}}<br>ABM ({scenario}): %{{y:.2f}}<extra></extra>'
        ))

# Calculate max for y-axis range
max_val = df_display['hts_value'].max()
for scenario in scenarios:
    if scenario in df_display.columns:
        max_val = max(max_val, df_display[scenario].max())

# Configure chart layout
fig.update_layout(
    barmode='group',
    xaxis_title='',
    yaxis_title='Rate',
    yaxis=dict(
        rangemode='tozero',
        range=[0, max_val * 1.15]  # Add 15% padding to prevent label cutoff
    ),
    margin=dict(t=50)  # Add top margin for label visibility
)

# Display data table and chart side by side
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    
    # Build column config dynamically based on selected scenarios
    column_config = {
        "metric": st.column_config.TextColumn("Metric"),
        "hts_value": st.column_config.NumberColumn("HTS", format="%.2f")
    }
    for scenario in scenarios:
        if scenario in df_display.columns:
            column_config[scenario] = st.column_config.NumberColumn(
                f"ABM {scenario}",
                format="%.2f"
            )
    
    st.dataframe(
        df_display,
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )

with separator_col:
    st.subheader("")  

with chart_col:
    st.subheader("📈 Rate Comparison")
    st.plotly_chart(fig, use_container_width=True)
