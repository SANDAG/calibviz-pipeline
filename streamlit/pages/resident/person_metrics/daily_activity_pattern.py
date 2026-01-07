import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Daily Activity Pattern Distribution", layout="wide")

st.title("Daily Activity Pattern")

display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT person_type, activity_pattern, abm_count, hts_count FROM calibration_metrics.daily_activity_pattern").fetch_df()

# prepare person type filter list
person_type_list = sorted(df['person_type'].unique().tolist())
selected_person_type = st.radio("Person Type", person_type_list, index=len(person_type_list)-1, horizontal=True)

# Filter data based on selected person type
df_filtered = df.copy()
df_display = df_filtered[df_filtered['person_type'] == selected_person_type]

total_abm = df_display['abm_count'].sum()
total_hts = df_display['hts_count'].sum()

df_display['abm_percentage'] = df_display['abm_count'] * 100 / total_abm if total_abm > 0 else 0
df_display['hts_percentage'] = df_display['hts_count'] * 100 / total_hts if total_hts > 0 else 0
df_display = df_display[['activity_pattern', 'hts_percentage', 'abm_percentage']]
df_display = df_display.sort_values(by='activity_pattern')

fig = go.Figure()

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['activity_pattern'],
    y=df_display['hts_percentage'],
    hovertemplate='Activity Pattern: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_display['activity_pattern'],
    y=df_display['abm_percentage'],
    hovertemplate='Activity Pattern: %{x}<br>ABM: %{y:.1f}%<extra></extra>'
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