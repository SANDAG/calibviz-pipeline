import streamlit as st
import sys
import plotly.graph_objects as go
import pandas as pd

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)
from scenario_config import (
    render_scenario_selector,
    render_survey_year_selector,
    format_scenario_sql_list
)

st.set_page_config(page_title="Mandatory Tour Length - InternalTrip", layout="wide")

st.title("Mandatory Tour Length - InternalTrip")

display_connection_status()

# Get scenario and survey year selections
scenarios = render_scenario_selector()
survey_years = render_survey_year_selector()

# Query and display data
conn = get_db_connection()

# Query the dbt model - all logic is now in the dbt model
scenarios_list = format_scenario_sql_list(scenarios)
query = f"""
    SELECT
        scenario,
        district,
        purpose,
        abm_avg_distance,
        hts_2022_avg_distance,
        hts_2023_avg_distance
    FROM calibration_metrics.mandatory_tour_length_InternalTrip
    WHERE scenario IN ('{scenarios_list}')
"""

df = conn.execute(query).fetch_df()

# Fill NaN values with 0
df = df.fillna(0)

# Prepare purpose filter list
purpose_list = sorted(df['purpose'].unique().tolist())

selected_purpose = st.radio("Purpose", purpose_list, index=0, horizontal=True)

# Filter data based on selected purpose
df_filtered = df[df['purpose'] == selected_purpose]

# Pivot data to have separate columns for each scenario
df_pivot = df_filtered.pivot_table(
    index='district',
    columns='scenario',
    values='abm_avg_distance',
    aggfunc='first'
).reset_index()

# Get HTS columns only for selected survey years
agg_dict = {}
for year in survey_years:
    col_name = f'hts_{year}_avg_distance'
    agg_dict[col_name] = 'first'

hts_cols = df_filtered.groupby('district').agg(agg_dict).reset_index()

# Merge with HTS data
df_display = df_pivot.merge(hts_cols, on='district', how='left')

# Fill NaN with 0
df_display = df_display.fillna(0)

# Sort districts (Total should be last)
district_order = sorted([d for d in df_display['district'].unique() if d != 'Total'])
if 'Total' in df_display['district'].values:
    district_order.append('Total')
df_display['district'] = df_display['district'].astype('category')
df_display['district'] = df_display['district'].cat.set_categories(district_order)
df_display = df_display.sort_values('district')

fig = go.Figure()

# Add ABM bars for each scenario
for scenario in scenarios:
    if scenario in df_display.columns:
        fig.add_trace(go.Bar(
            name=f'ABM ({scenario})',
            x=df_display['district'],
            y=df_display[scenario],
            hovertemplate=f'District: %{{x}}<br>ABM ({scenario}): %{{y:.2f}} miles<extra></extra>'
        ))

# Add HTS bars for each selected year
for year in survey_years:
    col_name = f'hts_{year}_avg_distance'
    if col_name in df_display.columns:
        fig.add_trace(go.Bar(
            name=f'HTS {year}',
            x=df_display['district'],
            y=df_display[col_name],
            hovertemplate=f'District: %{{x}}<br>HTS {year}: %{{y:.2f}} miles<extra></extra>'
        ))

fig.update_layout(
    barmode='group',
    xaxis_title='District',
    yaxis_title='Average Distance (miles)',
    hovermode='x unified'
)

# Display data
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    
    # Build column config dynamically based on selected scenarios and survey years
    column_config = {}
    
    for scenario in scenarios:
        if scenario in df_display.columns:
            column_config[scenario] = st.column_config.NumberColumn(
                f"ABM {scenario}",
                format="%.2f"
            )
    
    for year in survey_years:
        col_name = f'hts_{year}_avg_distance'
        if col_name in df_display.columns:
            column_config[col_name] = st.column_config.NumberColumn(
                f"HTS {year} Avg Distance",
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
    st.subheader("📈 Average Distance Comparison")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# DISTANCE DISTRIBUTION SECTION
# ============================================================
st.markdown("---")
st.header("📊 Distance Distribution by Bin")

# Query mandTLFD metric for distance distribution
scenarios_list = format_scenario_sql_list(scenarios)
query_dist = f"""
    SELECT
        scenario,
        distbin,
        district,
        purpose,
        abm_value,
        hts_2022_value,
        hts_2023_value
    FROM calibration_metrics.mandTLFD
    WHERE scenario IN ('{scenarios_list}')
    ORDER BY scenario, distbin
"""

df_dist = conn.execute(query_dist).fetch_df()

if not df_dist.empty:
    # District filter - add "Total" option
    district_list = sorted(df_dist['district'].unique().tolist())
    district_list.insert(0, "Total")
    selected_district = st.selectbox("Select District", district_list, index=0)
    
    # Filter by selected purpose and aggregate by district
    if selected_district == "Total":
        # Aggregate all districts
        df_dist_filtered = df_dist[df_dist['purpose'] == selected_purpose].groupby(['scenario', 'distbin']).agg({
            'abm_value': 'sum',
            'hts_2022_value': 'sum',
            'hts_2023_value': 'sum'
        }).reset_index()
    else:
        # Filter by selected district
        df_dist_filtered = df_dist[
            (df_dist['purpose'] == selected_purpose) & 
            (df_dist['district'] == selected_district)
        ]
    
    # Calculate proportions for visualization
    if not df_dist_filtered.empty:
        # Create line chart
        fig_dist = go.Figure()
        
        # Add ABM line for each scenario
        for scenario in scenarios:
            df_scenario = df_dist_filtered[df_dist_filtered['scenario'] == scenario].copy()
            if not df_scenario.empty:
                total_abm = df_scenario['abm_value'].sum()
                if total_abm > 0:
                    df_scenario['abm_proportion'] = (df_scenario['abm_value'] / total_abm) * 100
                else:
                    df_scenario['abm_proportion'] = 0
                
                fig_dist.add_trace(go.Scatter(
                    name=f'ABM ({scenario})',
                    x=df_scenario['distbin'],
                    y=df_scenario['abm_proportion'],
                    mode='lines+markers',
                    line=dict(width=2),
                    hovertemplate='Distance Bin: %{x}<br>Proportion: %{y:.2f}%<extra></extra>'
                ))
        
        # HTS lines for each selected survey year
        for year in survey_years:
            col_name = f'hts_{year}_value'
            df_hts = df_dist_filtered.groupby('distbin').agg({col_name: 'first'}).reset_index()
            total_hts = df_hts[col_name].sum()
            if total_hts > 0:
                df_hts['hts_proportion'] = (df_hts[col_name] / total_hts) * 100
            else:
                df_hts['hts_proportion'] = 0
                
            fig_dist.add_trace(go.Scatter(
                name=f'HTS {year}',
                x=df_hts['distbin'],
                y=df_hts['hts_proportion'],
                mode='lines+markers',
                line=dict(width=2),
                hovertemplate=f'Distance Bin: %{{x}}<br>Proportion: %{{y:.2f}}%<extra></extra>'
            ))
        
        fig_dist.update_layout(
            xaxis_title='Distance Bin (miles)',
            yaxis_title='Proportion (%)',
            hovermode='x unified',
            height=500
        )
        
        # Display
        dist_table_col, dist_sep_col, dist_chart_col = st.columns([1, 0.1, 2])
        
        with dist_table_col:
            st.subheader("📊 Distribution Data")
            
            # Prepare table with scenario columns
            display_data = []
            for distbin in sorted(df_dist_filtered['distbin'].unique()):
                row = {'distbin': distbin}
                for scenario in scenarios:
                    scenario_data = df_dist_filtered[(df_dist_filtered['scenario'] == scenario) & (df_dist_filtered['distbin'] == distbin)]
                    if not scenario_data.empty:
                        abm_val = scenario_data['abm_value'].values[0]
                        total = df_dist_filtered[df_dist_filtered['scenario'] == scenario]['abm_value'].sum()
                        row[f'{scenario}_pct'] = (abm_val / total * 100) if total > 0 else 0
                    else:
                        row[f'{scenario}_pct'] = 0
                
                # HTS data for each selected year
                for year in survey_years:
                    col_name = f'hts_{year}_value'
                    hts_data = df_dist_filtered[df_dist_filtered['distbin'] == distbin]
                    if not hts_data.empty:
                        hts_val = hts_data[col_name].values[0]
                        total_hts = df_dist_filtered.groupby('distbin').agg({col_name: 'first'})[col_name].sum()
                        row[f'hts_{year}_pct'] = (hts_val / total_hts * 100) if total_hts > 0 else 0
                    else:
                        row[f'hts_{year}_pct'] = 0
                    
                display_data.append(row)
            
            display_df = pd.DataFrame(display_data)
            
            # Build column config
            column_config = {
                "distbin": st.column_config.NumberColumn("Distance Bin", format="%d")
            }
            for scenario in scenarios:
                column_config[f'{scenario}_pct'] = st.column_config.NumberColumn(f"{scenario} %", format="%.2f")
            for year in survey_years:
                column_config[f'hts_{year}_pct'] = st.column_config.NumberColumn(f"HTS {year} %", format="%.2f")
            
            st.dataframe(
                display_df,
                column_config=column_config,
                use_container_width=True,
                hide_index=True,
                height=400
            )
        
        with dist_sep_col:
            st.subheader("")
        
        with dist_chart_col:
            st.subheader("📈 Distance Distribution")
            st.plotly_chart(fig_dist, use_container_width=True)
    else:
        st.warning(f"No distance distribution data available for {selected_purpose} in {selected_district}")
else:
    st.warning("No distance distribution data available")
