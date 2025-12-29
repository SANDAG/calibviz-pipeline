import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Trip and Tour Rates", layout="wide")

st.title("Trip and Tour Rates")

display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT metric, hts_value, abm_value FROM calibration_metrics.trip_tour_rates").fetch_df()

# Create chart - values are already in final format (no percentage conversion needed)
fig = go.Figure()

# Add HTS bars (Reference - using blue color similar to other charts)
fig.add_trace(go.Bar(
    name='HTS',
    x=df['metric'],
    y=df['hts_value'],
    marker_color='rgb(40,60,117)',  # Blue color
    text=df['hts_value'].round(2),
    textposition='outside',
    hovertemplate='%{x}<br>HTS: %{y:.2f}<extra></extra>'
))

# Add ABM bars (Model - using purple/red color similar to other charts)
fig.add_trace(go.Bar(
    name='ABM',
    x=df['metric'],
    y=df['abm_value'],
    marker_color='rgb(138,28,97)',  # Orange-red color
    text=df['abm_value'].round(2),
    textposition='outside',
    hovertemplate='%{x}<br>ABM: %{y:.2f}<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='',
    yaxis_title='Rate',
    yaxis=dict(
        rangemode='tozero',
        range=[0, df[['hts_value', 'abm_value']].max().max() * 1.15]  # Add 15% padding above max value
    ),
    margin=dict(t=50)  # Add top margin
)

# Display data
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    st.dataframe(
        df,
        column_config={
            "metric": st.column_config.TextColumn(
                "Metric"
            ),
            "hts_value": st.column_config.NumberColumn(
                "Reference",
                format="%.2f"
            ),
            "abm_value": st.column_config.NumberColumn(
                "Model",
                format="%.2f"
            )
        },
        use_container_width=True,
        hide_index=True
    )

with separator_col:
    st.subheader("")  

with chart_col:
    st.subheader("📈 Rate Comparison")
    st.plotly_chart(fig, use_container_width=True)
