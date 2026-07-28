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

df = conn.execute("SELECT district, purpose, abm_avg_distance, hts_avg_distance FROM calibration_metrics.mandatory_tour_length_InternalTrip").fetch_df()

# Prepare purpose filter list
purpose_list = sorted(df['purpose'].unique().tolist())

selected_purpose = st.radio("Purpose", purpose_list, index=0, horizontal=True)

# Filter data based on selected purpose
df_filtered = df.copy()
df_display = df_filtered[df_filtered['purpose'] == selected_purpose]

# Sort districts (Total should be last)
district_order = sorted([d for d in df_display['district'].unique() if d != 'Total'])
if 'Total' in df_display['district'].values:
    district_order.append('Total')
df_display['district'] = df_display['district'].astype('category')
df_display['district'] = df_display['district'].cat.set_categories(district_order)
df_display = df_display.sort_values('district')

fig = go.Figure()

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['district'],
    y=df_display['hts_avg_distance'],
    hovertemplate='District: %{x}<br>HTS: %{y:.2f} miles<extra></extra>'
))

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_display['district'],
    y=df_display['abm_avg_distance'],
    hovertemplate='District: %{x}<br>ABM: %{y:.2f} miles<extra></extra>'
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
    st.dataframe(
        df_display,
        column_config={
            "abm_avg_distance": st.column_config.NumberColumn(
                "ABM Avg Distance",
                format="%.2f"
            ),
            "hts_avg_distance": st.column_config.NumberColumn(
                "HTS Avg Distance",
                format="%.2f"
            )
        },
        use_container_width=True,
        hide_index=True
    )

with separator_col:
    st.subheader("")  

with chart_col:
    st.subheader("📈 Average Distance Comparison")
    st.plotly_chart(fig, use_container_width=True)
