import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Mandatory Tour Length - InternalTrip", layout="wide")

st.title("Mandatory Tour Length - InternalTrip")

display_connection_status()

# Query and display data
conn = get_db_connection()

# Survey year selector - allow multiple selections
st.markdown("### Select Survey Year(s)")
survey_years = st.multiselect(
    "Survey Years",
    options=["2022", "2023"],
    default=["2022"],
    label_visibility="collapsed"
)

if not survey_years:
    st.warning("Please select at least one survey year")
    st.stop()

# Query the dbt model - all logic is now in the dbt model
query = """
    SELECT
        district,
        purpose,
        abm_avg_distance,
        hts_2022_avg_distance,
        hts_2023_avg_distance
    FROM calibration_metrics.mandatory_tour_length_InternalTrip
"""

df = conn.execute(query).fetch_df()

# Fill NaN values with 0
df = df.fillna(0)

# Prepare purpose filter list
purpose_list = sorted(df['purpose'].unique().tolist())

selected_purpose = st.radio("Purpose", purpose_list, index=0, horizontal=True)

# Filter data based on selected purpose
df_filtered = df.copy()
df_display = df_filtered[df_filtered['purpose'] == selected_purpose]

# Select only the columns we need based on selected survey years
columns_to_keep = ['district', 'purpose', 'abm_avg_distance']
for year in survey_years:
    columns_to_keep.append(f'hts_{year}_avg_distance')
df_display = df_display[columns_to_keep]

# Sort districts (Total should be last)
district_order = sorted([d for d in df_display['district'].unique() if d != 'Total'])
if 'Total' in df_display['district'].values:
    district_order.append('Total')
df_display['district'] = df_display['district'].astype('category')
df_display['district'] = df_display['district'].cat.set_categories(district_order)
df_display = df_display.sort_values('district')

fig = go.Figure()

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_display['district'],
    y=df_display['abm_avg_distance'],
    hovertemplate='District: %{x}<br>ABM: %{y:.2f} miles<extra></extra>'
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
    
    # Build column config dynamically based on selected survey years
    column_config = {
        "abm_avg_distance": st.column_config.NumberColumn(
            "ABM Avg Distance",
            format="%.2f"
        )
    }
    
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
