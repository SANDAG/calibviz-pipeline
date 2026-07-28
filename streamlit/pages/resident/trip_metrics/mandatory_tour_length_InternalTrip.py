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

# Query ABM data (same for all survey years)
abm_query = """
    WITH abm3_persons_with_district AS (
        SELECT
            p.person_id,
            p.ptype,
            p.workplace_zone_id,
            p.school_zone_id,
            p.work_from_home,
            p.is_internal_worker,
            p.distance_to_work,
            p.distance_to_school,
            geo.pseudomsa as home_district
        FROM calibration_staging.stg_abm3_persons p
        LEFT JOIN calibration_seeds.mgra_taz_pmsa_xref geo ON p.home_zone_id = geo.mgra
    ),
    abm3_work AS (
        SELECT home_district, 'Work' AS purpose, AVG(distance_to_work) AS avg_distance
        FROM abm3_persons_with_district
        WHERE workplace_zone_id > 0 AND work_from_home = false AND is_internal_worker = true
        GROUP BY home_district
    ),
    abm3_university AS (
        SELECT home_district, 'University' AS purpose, AVG(distance_to_school) AS avg_distance
        FROM abm3_persons_with_district
        WHERE ptype = 3 AND school_zone_id > 0
        GROUP BY home_district
    ),
    abm3_school AS (
        SELECT home_district, 'School' AS purpose, AVG(distance_to_school) AS avg_distance
        FROM abm3_persons_with_district
        WHERE ptype >= 6 AND school_zone_id > 0
        GROUP BY home_district
    ),
    abm3_work_total AS (
        SELECT NULL AS home_district, 'Work' AS purpose, AVG(distance_to_work) AS avg_distance
        FROM abm3_persons_with_district
        WHERE workplace_zone_id > 0 AND work_from_home = false AND is_internal_worker = true
    ),
    abm3_university_total AS (
        SELECT NULL AS home_district, 'University' AS purpose, AVG(distance_to_school) AS avg_distance
        FROM abm3_persons_with_district
        WHERE ptype = 3 AND school_zone_id > 0
    ),
    abm3_school_total AS (
        SELECT NULL AS home_district, 'School' AS purpose, AVG(distance_to_school) AS avg_distance
        FROM abm3_persons_with_district
        WHERE ptype >= 6 AND school_zone_id > 0
    ),
    abm3_all AS (
        SELECT * FROM abm3_work
        UNION ALL SELECT * FROM abm3_university
        UNION ALL SELECT * FROM abm3_school
        UNION ALL SELECT * FROM abm3_work_total
        UNION ALL SELECT * FROM abm3_university_total
        UNION ALL SELECT * FROM abm3_school_total
    )
    SELECT
        COALESCE(d.pmsa_name, 'Total') AS district,
        a.purpose,
        a.avg_distance AS abm_avg_distance
    FROM abm3_all a
    LEFT JOIN calibration_seeds.pmsa_name d ON a.home_district = d.pmsa_id
"""

# Execute ABM query
df_abm = conn.execute(abm_query).fetch_df()

# Query HTS data for each selected year and merge
df = df_abm.copy()

for year in survey_years:
    # Determine which HTS staging table to use
    if year == "2022":
        hts_table = "stg_hts_mandTripLengths"
    else:
        hts_table = "stg_hts_2023_mandTripLengths"
    
    # Query HTS data
    hts_query = f"""
        SELECT
            "District" AS district,
            purpose,
            value AS hts_{year}_avg_distance
        FROM calibration_staging.{hts_table}
    """
    
    df_hts = conn.execute(hts_query).fetch_df()
    
    # Merge with main dataframe
    df = df.merge(df_hts, on=['district', 'purpose'], how='outer')

# Fill NaN values with 0
df = df.fillna(0)

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
