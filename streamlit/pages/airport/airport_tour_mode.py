import sys

import plotly.express as px

import streamlit as st

sys.path.append("..")

from database import display_connection_status, get_db_connection

st.set_page_config(page_title="Airport Tour Mode Comparison", layout="wide")

st.title("Airport Tour Mode Comparison")


display_connection_status()

# Query and display data
conn = get_db_connection()
df = conn.execute(
    "SELECT * FROM calibration_metrics.tour_share_by_mode WHERE scenario IS NOT NULL"
).fetch_df()

# Add multi-select for scenarios
available_scenarios = sorted(df["scenario"].unique())
scenario_filter = st.multiselect(
    "Select Scenarios to Compare",
    options=available_scenarios,
    default=available_scenarios,
)

if not scenario_filter:
    st.warning("Please select at least one scenario")
    st.stop()

df = df[df["scenario"].isin(scenario_filter)]

# Add filter for dimension
dimension_filter = st.selectbox(
    "Select Dimension (e.g. type to aggregate by)", options=df["dimension"].unique()
)
level_filter = st.selectbox(
    "Select Level (aggregated (visitor, resident), detailed (e.g. res_nb, vis_nb), total (by aggregated type), employee)",
    index=df["tour_type"].unique().tolist().index("total"),
    options=df["tour_type"].unique(),
)

if level_filter != "total":
    filtered_df = df[
        (df["dimension"] == dimension_filter)
        & (df["tour_type"] == level_filter)
        & (df["level"] != "total")
    ]
else:
    filtered_df = df[
        (df["dimension"] == dimension_filter)
        & (df["level"] == "total")
        & (df["dimension_value"] != "total")
    ]

with st.expander("View Filtered Data", expanded=False):
    st.dataframe(
        filtered_df,
        column_config={
            "survey_percentage": st.column_config.NumberColumn(format="%.2f%%"),
            "model_percentage": st.column_config.NumberColumn(format="%.2f%%"),
            "percentage_diff": st.column_config.NumberColumn(format="%.2f%%"),
        },
    )

# Add toggle for switching between percentage and count values
show_percentage = st.toggle("Show Percentage", value=True)

# Set y-axis columns based on toggle
if show_percentage:
    value_vars = ["survey_percentage", "model_percentage"]
    y_label = "Percentage"
    value_col = "percentage"
else:
    value_vars = ["survey_trip", "model_trip"]
    y_label = "Count"
    value_col = "count"

df_dimension = filtered_df.melt(
    id_vars=["scenario", "dimension_value"],
    value_vars=value_vars,
    var_name="source",
    value_name=value_col,
)

# Clean up source names to 'Survey' and 'Model'
# df_tour['source'] = df_tour['source'].str.replace('_percentage|_trip|_count', '', regex=True).str.replace('survey', 'Survey').str.replace('model', 'Model')
df_dimension["source"] = (
    df_dimension["source"]
    .str.replace("_percentage|_trip|_count", "", regex=True)
    .str.replace("survey", "Survey")
    .str.replace("model", "Model")
)
# Append scenario name to Model sources
mask = df_dimension["source"] == "Model"
df_dimension.loc[mask, "source"] = "Model (" + df_dimension.loc[mask, "scenario"] + ")"

df_dimension = df_dimension.drop(columns=["scenario"]).drop_duplicates()

# Chart 2: Breakdown by Dimension Value
st.write(f"### Breakdown by Dimension Value ({y_label})")

dimension_value_order = [
    "Pickup Dropoff",
    "Ridehail",
    "Taxi",
    "Drive and Park",
    "Shuttle Van",
    "Rental Car",
    "Transit",
]

# Create source order: Survey first, then all model scenarios
source_order = ["Survey"] + [f"Model ({s})" for s in sorted(scenario_filter)]

fig2 = px.bar(
    df_dimension,
    x="dimension_value",
    y=value_col,
    color="source",
    barmode="group",
    category_orders={"source": source_order, "dimension_value": dimension_value_order},
    labels={value_col: y_label, "dimension_value": "Dimension Value", "source": ""},
)

st.plotly_chart(fig2, use_container_width=True)
