import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Work From Home Distribution", layout="wide")

st.title("Work From Home Distribution")

display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT district, abm_proportion, hts_proportion FROM calibration_metrics.work_from_home").fetch_df()

df_display = df.copy()
df_display['hts_percentage'] = df_display['hts_proportion'] * 100
df_display['abm_percentage'] = df_display['abm_proportion'] * 100
df_display = df_display.drop(columns=['hts_proportion', 'abm_proportion'])

fig = go.Figure()

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['district'],
    y=df_display['hts_percentage'],
    hovertemplate='WFH Share: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_display['district'],
    y=df_display['abm_percentage'],
    hovertemplate='WFH Share: %{x}<br>ABM: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='District',
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
    