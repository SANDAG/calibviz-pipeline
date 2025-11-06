import streamlit as st
import sys
import plotly.graph_objects as go

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)

st.set_page_config(page_title="Airport Tour Mode Comparison", layout="wide")

st.title("Airport Tour Mode Comparison")


display_connection_status()

# Query and display data
conn = get_db_connection()
df = conn.execute("SELECT * FROM main_metrics.tour_share_by_mode").fetch_df()

# Add filter for dimension
dimension_filter = st.selectbox("Select Dimension", options=df['dimension'].unique())
level_filter = st.selectbox("Select Level", options=df['level'].unique())


filtered_df = df[(df['dimension'] == dimension_filter) & (df['level'] == level_filter)]

st.dataframe(filtered_df)
st.bar_chart(filtered_df, x='tour_type', y=['model_percentage', 'survey_percentage'],  stack=False)

st.bar_chart(filtered_df, x='dimension_value', y=['model_percentage', 'survey_percentage'],  stack=False)
