import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="District to District Flows", layout="wide")

st.title("District to District Flows")

display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT home_district, work_district, abm_total_workers, hts_total_workers FROM calibration_metrics.district_flows").fetch_df()

# prepare home district filter list
home_districts_list = sorted(df['home_district'].unique().tolist())
#total_label = next((item for item in home_districts_list if "Total" in item), home_districts_list[0])

selected_home_district = st.radio("Home District", home_districts_list, index=len(home_districts_list)-1, horizontal=True)

# Filter data based on selected home district
df_filtered = df.copy()
df_display = df_filtered[df_filtered['home_district'] == selected_home_district]

total_abm = df_display['abm_total_workers'].sum()
total_hts = df_display['hts_total_workers'].sum()

df_display['abm_percentage'] = df_display['abm_total_workers'] * 100 / total_abm if total_abm > 0 else 0
df_display['hts_percentage'] = df_display['hts_total_workers'] * 100 / total_hts if total_hts > 0 else 0

df_display = df_display[['work_district', 'hts_percentage', 'abm_percentage']]

fig = go.Figure()

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['work_district'],
    y=df_display['hts_percentage'],
    hovertemplate='Work District: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_display['work_district'],
    y=df_display['abm_percentage'],
    hovertemplate='Work District: %{x}<br>ABM: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Work District',
    yaxis_title='Percentage',
    yaxis_ticksuffix='%'
)

# Display data
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    st.dataframe(
        df_display,
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
    