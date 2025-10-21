import streamlit as st
import sys
sys.path.append('..')

from database import (
    get_db_connection,
    query_household_size,
    display_connection_status
)

st.set_page_config(page_title="Trip Mode Distribution", layout="wide")

st.title("Trip Mode")


display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT trip_mode, abm_share, hts_share FROM main.trip_mode ORDER BY trip_mode").fetch_df()


# Display data
st.subheader("📊 Data Table")
df_display = df.copy()
df_display['abm_percentage'] = df_display['abm_share'] * 100
df_display['hts_percentage'] = df_display['hts_share'] * 100
df_display = df_display.drop(columns=['abm_share', 'hts_share'])

st.dataframe(
    df_display,
    column_config={
        "abm_percentage": st.column_config.NumberColumn(
            "ABM Percentage",
            format="%.2f%%"
        ),
        "hts_percentage": st.column_config.NumberColumn(
            "HTS Percentage",
            format="%.2f%%"
        )
    },
    use_container_width=True
)


st.divider()

# Display chart
st.subheader("📈 Distribution Comparison")
st.bar_chart(df_display, x='trip_mode', y=['abm_percentage', 'hts_percentage'], stack=False)