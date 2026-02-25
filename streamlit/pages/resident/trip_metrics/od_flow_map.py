import sys
import pandas as pd
import pydeck as pdk
import streamlit as st

sys.path.append("..")

from database import display_connection_status, get_db_connection

st.set_page_config(page_title="OD Flow Map", layout="wide", initial_sidebar_state="expanded")

st.title("🗺️ Origin-Destination Flow Map")
st.markdown(
    "Interactive visualization of trip flows between TAZ (Traffic Analysis Zones). "
    "Arc width and color represent trip volumes."
)

display_connection_status()

# Load data from database
conn = get_db_connection()

@st.cache_data(ttl=600)
def load_od_data():
    """Load OD flow data with caching"""
    query = """
    SELECT 
        origin_taz,
        destination_taz,
        trip_mode,
        mode_name,
        trip_period,
        trip_count,
        weighted_trips,
        avg_distance_miles,
        avg_time_minutes,
        origin_lon,
        origin_lat,
        origin_name,
        dest_lon,
        dest_lat,
        dest_name
    FROM calibration_metrics.od_flow_map
    WHERE weighted_trips >= 0.1  -- Filter out very small flows
    """
    return conn.execute(query).fetch_df()

try:
    df = load_od_data()
    
    if df.empty:
        st.warning("⚠️ No OD flow data found. Please run the DBT model first: `dbt run --select od_flow_map`")
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Mode filter
    available_modes = sorted(df['mode_name'].dropna().unique())
    if available_modes:
        selected_modes = st.sidebar.multiselect(
            "Trip Mode",
            options=available_modes,
            default=available_modes[:3] if len(available_modes) >= 3 else available_modes
        )
    else:
        selected_modes = []
        st.sidebar.warning("No modes available")
    
    # Time period filter
    available_periods = sorted(df['trip_period'].dropna().unique())
    if available_periods:
        selected_periods = st.sidebar.multiselect(
            "Time Period",
            options=available_periods,
            default=available_periods
        )
    else:
        selected_periods = []
    
    # Flow threshold slider
    max_trips = float(df['weighted_trips'].max())
    min_trips = float(df['weighted_trips'].min())
    
    trip_threshold = st.sidebar.slider(
        "Minimum Trip Volume",
        min_value=min_trips,
        max_value=min(max_trips, 100.0),  # Cap display at 100 for better UX
        value=min(1.0, max_trips),
        step=0.5,
        help="Show only flows with at least this many trips"
    )
    
    # Top N flows
    top_n = st.sidebar.slider(
        "Show Top N Flows",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
        help="Limit display to top N flows by volume for better performance"
    )
    
    # Apply filters
    df_filtered = df.copy()
    
    if selected_modes:
        df_filtered = df_filtered[df_filtered['mode_name'].isin(selected_modes)]
    
    if selected_periods:
        df_filtered = df_filtered[df_filtered['trip_period'].isin(selected_periods)]
    
    df_filtered = df_filtered[df_filtered['weighted_trips'] >= trip_threshold]
    
    # Aggregate by OD pair (sum across modes/periods if multiple selected)
    df_aggregated = df_filtered.groupby(
        ['origin_taz', 'destination_taz', 'origin_lon', 'origin_lat', 
         'origin_name', 'dest_lon', 'dest_lat', 'dest_name'],
        as_index=False
    ).agg({
        'weighted_trips': 'sum',
        'trip_count': 'sum',
        'avg_distance_miles': 'mean',
        'avg_time_minutes': 'mean'
    })
    
    # Sort and limit to top N
    df_aggregated = df_aggregated.sort_values('weighted_trips', ascending=False).head(top_n)
    
    if df_aggregated.empty:
        st.warning("No flows match the selected filters. Try adjusting the filters.")
        st.stop()
    
    # Calculate statistics for display
    total_trips = df_aggregated['weighted_trips'].sum()
    total_od_pairs = len(df_aggregated)
    avg_distance = df_aggregated['avg_distance_miles'].mean()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Trips", f"{total_trips:,.0f}")
    with col2:
        st.metric("OD Pairs Shown", f"{total_od_pairs:,}")
    with col3:
        st.metric("Avg Distance", f"{avg_distance:.1f} mi")
    with col4:
        st.metric("Max Flow", f"{df_aggregated['weighted_trips'].max():.0f} trips")
    
    st.divider()
    
    # Prepare data for PyDeck
    # Normalize trip volumes for visual scaling
    max_flow = df_aggregated['weighted_trips'].max()
    min_flow = df_aggregated['weighted_trips'].min()
    
    df_aggregated['width_scale'] = 1 + 9 * (
        (df_aggregated['weighted_trips'] - min_flow) / (max_flow - min_flow)
    )
    
    # Create arc layer data
    arc_data = df_aggregated.rename(columns={
        'origin_lon': 'start_lon',
        'origin_lat': 'start_lat',
        'dest_lon': 'end_lon',
        'dest_lat': 'end_lat'
    })
    
    # Define PyDeck layers
    arc_layer = pdk.Layer(
        "ArcLayer",
        data=arc_data,
        get_source_position=['start_lon', 'start_lat'],
        get_target_position=['end_lon', 'end_lat'],
        get_source_color=[0, 128, 255, 140],  # Blue for origins
        get_target_color=[255, 128, 0, 140],  # Orange for destinations
        get_width='width_scale',
        width_min_pixels=1,
        width_max_pixels=10,
        pickable=True,
        auto_highlight=True,
    )
    
    # Create scatter layer for TAZ centroids
    taz_origins = df_aggregated[['origin_lon', 'origin_lat', 'origin_taz', 'origin_name']].drop_duplicates()
    taz_origins.columns = ['lon', 'lat', 'taz', 'name']
    
    taz_dests = df_aggregated[['dest_lon', 'dest_lat', 'destination_taz', 'dest_name']].drop_duplicates()
    taz_dests.columns = ['lon', 'lat', 'taz', 'name']
    
    all_taz = pd.concat([taz_origins, taz_dests]).drop_duplicates(subset=['taz'])
    
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=all_taz,
        get_position=['lon', 'lat'],
        get_radius=200,
        get_fill_color=[255, 0, 0, 160],
        pickable=True,
        auto_highlight=True,
    )
    
    # Calculate view state (center of all points)
    view_state = pdk.ViewState(
        longitude=arc_data[['start_lon', 'end_lon']].values.mean(),
        latitude=arc_data[['start_lat', 'end_lat']].values.mean(),
        zoom=10,
        pitch=45,
        bearing=0,
    )
    
    # Define tooltip
    tooltip = {
        "html": """
        <b>Flow:</b> {origin_name} → {dest_name}<br/>
        <b>Origin TAZ:</b> {origin_taz}<br/>
        <b>Destination TAZ:</b> {destination_taz}<br/>
        <b>Trips:</b> {weighted_trips:.1f}<br/>
        <b>Avg Distance:</b> {avg_distance_miles:.1f} miles<br/>
        <b>Avg Time:</b> {avg_time_minutes:.1f} minutes
        """,
        "style": {
            "backgroundColor": "steelblue",
            "color": "white",
            "fontSize": "12px",
            "padding": "10px"
        }
    }
    
    # Render map
    r = pdk.Deck(
        layers=[arc_layer, scatter_layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="mapbox://styles/mapbox/light-v10",
    )
    
    st.pydeck_chart(r)
    
    # Show data table below map
    with st.expander("📊 View Flow Data Table", expanded=False):
        display_df = df_aggregated[[
            'origin_taz', 'origin_name', 'destination_taz', 'dest_name',
            'weighted_trips', 'trip_count', 'avg_distance_miles', 'avg_time_minutes'
        ]].copy()
        
        display_df.columns = [
            'Origin TAZ', 'Origin', 'Dest TAZ', 'Destination',
            'Weighted Trips', 'Trip Count', 'Avg Distance (mi)', 'Avg Time (min)'
        ]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download option
        csv = display_df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="od_flows.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"❌ Error loading data: {str(e)}")
    st.info("💡 Make sure to run: `dbt seed` and `dbt run --select od_flow_map`")
    import traceback
    with st.expander("🔍 Error Details"):
        st.code(traceback.format_exc())
