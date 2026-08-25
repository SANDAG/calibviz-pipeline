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

st.set_page_config(page_title="Transit Pass Ownership Distribution", layout="wide")

st.title("Transit Pass Ownership")

display_connection_status()

# Get scenario selection
scenarios = render_scenario_selector()

# Query and display data
conn = get_db_connection()

scenarios_list = format_scenario_sql_list(scenarios)
df = conn.execute(f"SELECT scenario, person_type, abm_proportion, hts_proportion FROM calibration_metrics.transit_pass_ownership WHERE scenario IN ('{scenarios_list}')").fetch_df()

# Pivot ABM data by scenario
df_pivot_abm = df.pivot_table(
    index='person_type',
    columns='scenario',
    values='abm_proportion',
    aggfunc='first'
).reset_index()

# Get HTS data (same across scenarios)
df_hts = df.groupby('person_type').agg({
    'hts_proportion': 'first'
}).reset_index()

# Merge ABM and HTS data
df_display = df_pivot_abm.merge(df_hts, on='person_type', how='left')

# Convert to percentages
for scenario in scenarios:
    if scenario in df_display.columns:
        df_display[f'{scenario}_pct'] = df_display[scenario] * 100
        df_display = df_display.drop(columns=[scenario])

df_display['hts_percentage'] = df_display['hts_proportion'] * 100
df_display = df_display.drop(columns=['hts_proportion'])

fig = go.Figure()

# Add ABM bars for each scenario
for scenario in scenarios:
    col_name = f'{scenario}_pct'
    if col_name in df_display.columns:
        fig.add_trace(go.Bar(
            name=f'ABM ({scenario})',
            x=df_display['person_type'],
            y=df_display[col_name],
            hovertemplate=f'Person Type: %{{x}}<br>ABM ({scenario}): %{{y:.1f}}%<extra></extra>'
        ))

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['person_type'],
    y=df_display['hts_percentage'],
    hovertemplate='Person Type: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Person Type',
    yaxis_title='Percentage',
    yaxis_ticksuffix='%'
)

# Display data
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    
    # Build column config dynamically based on selected scenarios
    column_config = {}
    for scenario in scenarios:
        col_name = f'{scenario}_pct'
        if col_name in df_display.columns:
            column_config[col_name] = st.column_config.NumberColumn(
                f"ABM {scenario} %",
                format="%.1f%%"
            )
    
    column_config["hts_percentage"] = st.column_config.NumberColumn(
        "HTS Percentage",
        format="%.1f%%"
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
    st.subheader("📈 Distribution Comparison")
    st.plotly_chart(fig, use_container_width=True)