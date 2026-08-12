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

st.set_page_config(page_title="Daily Activity Pattern Distribution", layout="wide")

st.title("Daily Activity Pattern")

display_connection_status()

# Get scenario selection
scenarios = render_scenario_selector()

# Query and display data
conn = get_db_connection()

scenarios_list = format_scenario_sql_list(scenarios)
df = conn.execute(f"SELECT scenario, person_type, activity_pattern, abm_count, hts_count FROM calibration_metrics.daily_activity_pattern WHERE scenario IN ('{scenarios_list}')").fetch_df()

# prepare person type filter list
person_type_list = sorted(df['person_type'].unique().tolist())
selected_person_type = st.radio("Person Type", person_type_list, index=len(person_type_list)-1, horizontal=True)

# Filter data based on selected person type
df_filtered = df[df['person_type'] == selected_person_type]

# Pivot ABM data by scenario
df_pivot_abm = df_filtered.pivot_table(
    index='activity_pattern',
    columns='scenario',
    values='abm_count',
    aggfunc='sum'
).reset_index()

# Get HTS data (same across scenarios)
df_hts = df_filtered.groupby('activity_pattern').agg({
    'hts_count': 'first'
}).reset_index()

# Merge ABM and HTS data
df_display = df_pivot_abm.merge(df_hts, on='activity_pattern', how='left')

# Calculate percentages for each scenario
for scenario in scenarios:
    if scenario in df_display.columns:
        total_abm = df_display[scenario].sum()
        df_display[f'{scenario}_pct'] = df_display[scenario] * 100 / total_abm if total_abm > 0 else 0
        df_display = df_display.drop(columns=[scenario])

total_hts = df_display['hts_count'].sum()
df_display['hts_percentage'] = df_display['hts_count'] * 100 / total_hts if total_hts > 0 else 0
df_display = df_display.drop(columns=['hts_count'])
df_display = df_display.sort_values(by='activity_pattern')

fig = go.Figure()

# Add ABM bars for each scenario
for scenario in scenarios:
    col_name = f'{scenario}_pct'
    if col_name in df_display.columns:
        fig.add_trace(go.Bar(
            name=f'ABM ({scenario})',
            x=df_display['activity_pattern'],
            y=df_display[col_name],
            hovertemplate=f'Activity Pattern: %{{x}}<br>ABM ({scenario}): %{{y:.1f}}%<extra></extra>'
        ))

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['activity_pattern'],
    y=df_display['hts_percentage'],
    hovertemplate='Activity Pattern: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Activity Pattern',
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