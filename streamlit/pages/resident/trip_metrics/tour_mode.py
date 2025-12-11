import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Tour Mode Distribution", layout="wide")

st.title("Tour Mode Comparison")

display_connection_status()

# Query and display data
conn = get_db_connection()
df = conn.execute("SELECT tour_mode, veh_ownership_category, purpose, abm_tours, hts_tours FROM calibration_metrics.tour_mode ORDER BY tour_mode").fetch_df()

# Prepare filter lists
tour_modes_list = sorted(df['tour_mode'].unique(), key=lambda x: int(x.split(':')[0]))
veh_ownership_cat_list = sorted(df['veh_ownership_category'].unique(), key=lambda x: int(x.split(':')[0]))
purpose_list = sorted(df['purpose'].unique(), key=lambda x: int(x.split(':')[0]))

# Initialize selected lists
selected_tour_modes = []
selected_veh_ownership_cats = []
selected_purposes = []

# Initialize checkboxes in session state
if 'tour_mode_initialized' not in st.session_state:
    st.session_state.tour_mode_initialized = True
    for mode in tour_modes_list:
        st.session_state[f"m_{mode}"] = True
    for cat in veh_ownership_cat_list:
        st.session_state[f"c_{cat}"] = True
    for purp in purpose_list:
        st.session_state[f"p_{purp}"] = True

# === FILTERS SECTION (Collapsible at top) ===
with st.expander("🔍 Filters", expanded=False):
    if st.button("🔄 Reset Filters", use_container_width=False):
        for mode in tour_modes_list:
            st.session_state[f"m_{mode}"] = True
        
        for cat in veh_ownership_cat_list:
            st.session_state[f"c_{cat}"] = True
        
        for purp in purpose_list:
            st.session_state[f"p_{purp}"] = True

        st.rerun()
    
    st.divider()

    filter_cols = st.columns(3)
    
    # Tour Mode Filter
    with filter_cols[0]:
        st.markdown("**Tour Mode**")
        for mode in tour_modes_list:
            if st.checkbox(mode, key=f"m_{mode}"):
                selected_tour_modes.append(mode)
    
    # Ownership Category Filter
    with filter_cols[1]:
        st.markdown("**Vehicle Ownership**")
        for cat in veh_ownership_cat_list:
            if st.checkbox(cat, key=f"c_{cat}"):
                selected_veh_ownership_cats.append(cat)
    
    # Purpose Filter
    with filter_cols[2]:
        st.markdown("**Purpose**")
        for purp in purpose_list:
            if st.checkbox(purp, key=f"p_{purp}"):
                selected_purposes.append(purp)

# Apply filters
df_filtered = df.copy()
if selected_tour_modes:
    df_filtered = df_filtered[df_filtered['tour_mode'].isin(selected_tour_modes)]
if selected_veh_ownership_cats:
    df_filtered = df_filtered[df_filtered['veh_ownership_category'].isin(selected_veh_ownership_cats)]
if selected_purposes:
    df_filtered = df_filtered[df_filtered['purpose'].isin(selected_purposes)]

df_filtered = df_filtered.groupby('tour_mode', as_index=False).agg({
    'abm_tours': 'sum',
    'hts_tours': 'sum'
})

# Calculate shares
total_abm = df_filtered['abm_tours'].sum()
total_hts = df_filtered['hts_tours'].sum()

df_filtered['abm_percentage'] = df_filtered['abm_tours'] * 100 / total_abm if total_abm > 0 else 0
df_filtered['hts_percentage'] = df_filtered['hts_tours'] * 100 / total_hts if total_hts > 0 else 0

# Keep only tour_mode and shares
df_filtered = df_filtered[['tour_mode', 'hts_percentage', 'abm_percentage']]

fig = go.Figure()

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_filtered['tour_mode'],
    y=df_filtered['hts_percentage'],
    hovertemplate='Tour Mode: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

# Add ABM bars
fig.add_trace(go.Bar(
    name='ABM',
    x=df_filtered['tour_mode'],
    y=df_filtered['abm_percentage'],
    hovertemplate='Tour Mode: %{x}<br>ABM: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Tour Mode',
    yaxis_title='Percentage',
    xaxis_tickangle=45,
    yaxis_ticksuffix='%'
)

# === MAIN CONTENT: Chart and Table side by side ===
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")   
    
    st.dataframe(
        df_filtered,
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
    