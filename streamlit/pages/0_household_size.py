import streamlit as st
import sys
sys.path.append('..')

from database import (
    get_db_connection,
    query_household_size,
    display_connection_status
)

st.set_page_config(page_title="Household Size Distribution", layout="wide")

st.title("Household Size Distribution")


display_connection_status()

# Query and display data
conn = get_db_connection()

df = conn.execute("SELECT hhsize, abm_proportion, hts_proportion FROM main.hhsize").fetch_df()


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
st.bar_chart(df_display, x='hhsize', y=['abm_percentage', 'hts_percentage'], stack=False)