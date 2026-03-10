import streamlit as st
import sys
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Airport Tour Mode Comparison", layout="wide")

st.title("Airport Tour Mode Comparison")


display_connection_status()

# Query and display data
conn = get_db_connection()
df = conn.execute("SELECT * FROM calibration_metrics.tour_share_by_mode WHERE scenario IS NOT NULL").fetch_df()

# Add multi-select for scenarios
available_scenarios = sorted(df['scenario'].unique())
scenario_filter = st.multiselect(
    "Select Scenarios to Compare", 
    options=available_scenarios,
    default=available_scenarios
)

if not scenario_filter:
    st.warning("Please select at least one scenario")
    st.stop()

df = df[df['scenario'].isin(scenario_filter)]

# Add filter for dimension
dimension_filter = st.selectbox("Select Dimension (e.g. type to aggregate by)", options=df['dimension'].unique())
level_filter = st.selectbox("Select Level (aggregated (visitor, resident), detailed (e.g. res_nb, vis_nb), total (by aggregated type), employee)", index=df['tour_type'].unique().tolist().index('total'), options=df['tour_type'].unique())

if level_filter != 'total':
    filtered_df = df[(df['dimension'] == dimension_filter) & (df['tour_type'] == level_filter) & (df['level'] != 'total')]
else:
    filtered_df = df[(df['dimension'] == dimension_filter) & (df['level'] == 'total') & (df['dimension_value'] != 'total')]

with st.expander("View Filtered Data", expanded=False):
    st.dataframe(filtered_df, column_config={\
        "survey_percentage": st.column_config.NumberColumn(format="%.2f%%"),
        "model_percentage": st.column_config.NumberColumn(format="%.2f%%"),
        "percentage_diff": st.column_config.NumberColumn(format="%.2f%%"),
    })

# Add toggle for switching between percentage and count values
show_percentage = st.toggle("Show Percentage", value=True)

# Set y-axis columns based on toggle
if show_percentage:
    y_label = "Percentage"
    value_col = 'percentage'
else:
    y_label = "Count"
    value_col = 'count'

# Prepare data for visualization
viz_data = []
for _, row in filtered_df.iterrows():
    dimension_value = row['dimension_value']
    
    # Add survey data once
    if show_percentage:
        viz_data.append({
            'dimension_value': dimension_value,
            'source': 'Survey',
            value_col: row['survey_percentage']
        })
    else:
        viz_data.append({
            'dimension_value': dimension_value,
            'source': 'Survey',
            value_col: row['survey_trip']
        })
    
    # Add model data for this scenario
    scenario_name = row['scenario']
    if show_percentage:
        viz_data.append({
            'dimension_value': dimension_value,
            'source': f'Model ({scenario_name})',
            value_col: row['model_percentage']
        })
    else:
        viz_data.append({
            'dimension_value': dimension_value,
            'source': f'Model ({scenario_name})',
            value_col: row['model_trip']
        })

df_dimension = pd.DataFrame(viz_data)

# Remove duplicates from survey (it's repeated for each scenario)
df_dimension = df_dimension.drop_duplicates()

# Chart 2: Breakdown by Dimension Value
st.write(f"### Breakdown by Dimension Value ({y_label})")

dimension_value_order = ['Pickup Dropoff', 
                   'Ridehail', 
                   'Taxi', 
                   'Drive and Park', 
                   'Shuttle Van', 
                   'Rental Car', 
                   'Transit']

# Create source order: Survey first, then all model scenarios
source_order = ['Survey'] + [f'Model ({s})' for s in sorted(scenario_filter)]

fig2 = px.bar(
    df_dimension,
    x='dimension_value',
    y=value_col,
    color='source',
    barmode='group',
    category_orders={'source': source_order,
                     'dimension_value': dimension_value_order},
    labels={value_col: y_label, 'dimension_value': 'Dimension Value', 'source': ''}
)

st.plotly_chart(fig2, use_container_width=True)