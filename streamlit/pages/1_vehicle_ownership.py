import streamlit as st
import sys
sys.path.append('..')


from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Vehicle Ownership Distribution", layout="wide")


st.title("Vehicle Ownership")


display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT auto_ownership, abm_proportion, hts_proportion FROM main.auto_ownership").fetch_df()


# Display data
st.subheader("📊 Data Table")
df_display = df.copy()
df_display['abm_percentage'] = df_display['abm_proportion'] * 100
df_display['hts_percentage'] = df_display['hts_proportion'] * 100
df_display = df_display.drop(columns=['abm_proportion', 'hts_proportion'])

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
   width=800
)


st.divider()




# Display chart
import plotly.graph_objects as go

# Display chart
st.subheader("📈 Distribution Comparison")

fig = go.Figure()

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_display['auto_ownership'],
    y=df_display['abm_percentage'],
    hovertemplate='Household Size: %{x}<br>ABM: %{y:.1f}%<extra></extra>'
))

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display['auto_ownership'],
    y=df_display['hts_percentage'],
    hovertemplate='Household Size: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Household Size',
    yaxis_title='Percentage',
    xaxis_tickangle=-45,
    yaxis_ticksuffix='%'
)

# Control width using Streamlit container
col1, col2 = st.columns([4, 1])
with col1:
    st.plotly_chart(fig, use_container_width=True)