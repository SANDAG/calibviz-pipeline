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
dimension_filter = st.selectbox("Select Dimension (e.g. type to aggregate by)", options=df['dimension'].unique())
level_filter = st.selectbox("Select Level (aggregated (visitor, resident), detailed (e.g. res_nb, vis_nb), total (by aggregated type), employee)", options=df['level'].unique())

filtered_df = df[(df['dimension'] == dimension_filter) & (df['level'] == level_filter)]

st.dataframe(filtered_df)

# Add toggle for switching between percentage and count values
show_percentage = st.toggle("Show Percentage", value=True)

# Set y-axis columns based on toggle
if show_percentage:
    y_cols = ['model_percentage', 'survey_percentage']
    y_label = "Percentage"
else:
    y_cols = ['model_trip', 'survey_trip']  # Adjust these column names to match your data
    y_label = "Count"

st.write(f"### Breakdown by Tour Type ({y_label})")
st.bar_chart(filtered_df, x='tour_type', y=y_cols, stack=False)

st.write(f"### Breakdown by Dimension Value ({y_label})")
st.bar_chart(filtered_df, x='dimension_value', y=y_cols, stack=False)
