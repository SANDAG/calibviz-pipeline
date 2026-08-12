import streamlit as st
import sys
import plotly.graph_objects as go
import pandas as pd
import numpy as np

sys.path.append('..')

from database import (
    get_db_connection,
    display_connection_status
)
from scenario_config import (
    render_scenario_selector,
    format_scenario_sql_list
)

st.set_page_config(page_title="District to District Flows", layout="wide")

st.title("District to District Flows")

display_connection_status()

# Get scenario selection
scenarios = render_scenario_selector()

# Query and display data
conn = get_db_connection()

scenarios_list = format_scenario_sql_list(scenarios)
df = conn.execute(f"""
    SELECT scenario, home_district, work_district, abm_total_workers, hts_total_workers 
    FROM calibration_metrics.district_flows
    WHERE scenario IN ('{scenarios_list}')
""").fetch_df()

# prepare home district filter list
home_districts_list = sorted(df['home_district'].unique().tolist())

selected_home_district = st.radio("Home District", home_districts_list, index=len(home_districts_list)-1, horizontal=True)

# Filter data based on selected home district and pivot by scenario
df_filtered = df[df['home_district'] == selected_home_district]

# Pivot to get ABM data for each scenario
df_pivot_abm = df_filtered.pivot_table(
    index='work_district',
    columns='scenario',
    values='abm_total_workers',
    aggfunc='first'
).reset_index()

# Get HTS data (same across scenarios)
df_hts = df_filtered.groupby('work_district').agg({
    'hts_total_workers': 'first'
}).reset_index()

# Merge ABM and HTS data
df_display = df_pivot_abm.merge(df_hts, on='work_district', how='left')

# Fill NaN with 0
df_display = df_display.fillna(0)

# Calculate percentages
for scenario in scenarios:
    if scenario in df_display.columns:
        total_abm = df_display[scenario].sum()
        df_display[f'{scenario}_pct'] = df_display[scenario] * 100 / total_abm if total_abm > 0 else 0

total_hts = df_display['hts_total_workers'].sum()
df_display['hts_percentage'] = df_display['hts_total_workers'] * 100 / total_hts if total_hts > 0 else 0

# Create display columns list
display_cols = ['work_district']
for scenario in scenarios:
    if f'{scenario}_pct' in df_display.columns:
        display_cols.append(f'{scenario}_pct')
display_cols.append('hts_percentage')

df_display_table = df_display[display_cols]

fig = go.Figure()

# Add ABM bars for each scenario
for scenario in scenarios:
    col_name = f'{scenario}_pct'
    if col_name in df_display.columns:
        fig.add_trace(go.Bar(
            name=f'ABM ({scenario})',
            x=df_display_table['work_district'],
            y=df_display_table[col_name],
            hovertemplate=f'Work District: %{{x}}<br>ABM ({scenario}): %{{y:.1f}}%<extra></extra>'
        ))

# Add HTS bars
fig.add_trace(go.Bar(
    name='HTS',
    x=df_display_table['work_district'],
    y=df_display_table['hts_percentage'],
    hovertemplate='Work District: %{x}<br>HTS: %{y:.1f}%<extra></extra>'
))

fig.update_layout(
    barmode='group',
    xaxis_title='Work District',
    yaxis_title='Percentage',
    yaxis_ticksuffix='%'
)

# Display data
table_col, separator_col, chart_col = st.columns([1, 0.1, 2])

with table_col:
    st.subheader("📊 Data Table")
    
    # Build column config dynamically based on selected scenarios
    column_config = {}
    for scenario in scenarios:
        col_name = f'{scenario}_pct'
        if col_name in df_display_table.columns:
            column_config[col_name] = st.column_config.NumberColumn(
                f"ABM {scenario} %",
                format="%.1f%%"
            )
    
    column_config["hts_percentage"] = st.column_config.NumberColumn(
        "HTS Percentage",
        format="%.1f%%"
    )
    
    st.dataframe(
        df_display_table,
        column_config=column_config,
        use_container_width=True,
        hide_index=True
    )

with separator_col:
    st.subheader("")  

with chart_col:
    st.subheader("📈 Distribution Comparison")
    st.plotly_chart(fig, use_container_width=True)

# ============================================================
# ORIGIN-DESTINATION MATRIX SECTION
# ============================================================
st.markdown("---")
st.header("🗺️ Origin-Destination Flow Matrix")

# Create tabs for each scenario plus difference tab if multiple scenarios
if len(scenarios) > 1:
    tab_labels = [f"ABM {scenario}" for scenario in scenarios] + ["Difference"]
    matrix_tabs = st.tabs(tab_labels)
else:
    matrix_tabs = [st.container()]

# Show individual scenario matrices
for idx, scenario in enumerate(scenarios):
    with matrix_tabs[idx]:
        # Filter data for this scenario, excluding Total
        df_scenario = df[df['scenario'] == scenario].copy()
        df_scenario_no_total = df_scenario[df_scenario['home_district'] != 'Total']
        
        # Create pivot table for matrix
        matrix_data = df_scenario_no_total.pivot_table(
            index='home_district',
            columns='work_district',
            values='abm_total_workers',
            aggfunc='sum',
            fill_value=0
        )
        
        # Sort index and columns
        matrix_data = matrix_data.sort_index()
        matrix_data = matrix_data[sorted(matrix_data.columns)]
        
        # Add row totals
        matrix_data['Total'] = matrix_data.sum(axis=1)
        
        # Add column totals
        col_totals = matrix_data.sum(axis=0)
        matrix_data.loc['Total'] = col_totals
        
        # Display options
        col1, col2 = st.columns([1, 3])
        with col1:
            display_mode = st.radio(
                "Display Mode",
                ["Counts", "Percentages"],
                key=f"display_mode_{scenario}_{idx}",
                horizontal=True
            )
        
        with col2:
            if display_mode == "Percentages":
                pct_base = st.radio(
                    "Percentage Base",
                    ["Row Total", "Column Total", "Grand Total"],
                    key=f"pct_base_{scenario}_{idx}",
                    horizontal=True
                )
        
        # Create display matrix
        if display_mode == "Counts":
            display_matrix = matrix_data.copy()
            format_str = "%.0f"
        else:
            # Calculate percentages
            if pct_base == "Row Total":
                # Percentage of row total (each row sums to 100%)
                display_matrix = matrix_data.div(matrix_data['Total'], axis=0) * 100
                display_matrix['Total'] = 100.0  # Row totals are 100%
                display_matrix.loc['Total'] = matrix_data.loc['Total'].div(matrix_data.loc['Total', 'Total']) * 100
            elif pct_base == "Column Total":
                # Percentage of column total (each column sums to 100%)
                display_matrix = matrix_data.div(matrix_data.loc['Total'], axis=1) * 100
                display_matrix.loc['Total'] = 100.0  # Column totals are 100%
            else:  # Grand Total
                # Percentage of grand total
                grand_total = matrix_data.loc['Total', 'Total']
                display_matrix = (matrix_data / grand_total) * 100
            
            format_str = "%.1f"
        
        # Style the dataframe
        st.subheader(f"📊 {scenario} Flow Matrix ({display_mode})")
        
        # Create column config for formatting
        column_config = {}
        for col in display_matrix.columns:
            if display_mode == "Counts":
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.0f"
                )
            else:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.1f%%"
                )
        
        # Display the matrix
        st.dataframe(
            display_matrix,
            column_config=column_config,
            use_container_width=True,
            height=400
        )
        
        # Add summary statistics
        st.caption(f"**Total Workers:** {int(matrix_data.loc['Total', 'Total']):,}")

# Show difference tab if multiple scenarios
if len(scenarios) > 1:
    with matrix_tabs[-1]:  # Last tab is the difference tab
        st.subheader("🔄 Scenario Comparison")
        
        # Scenario selectors
        col1, col2 = st.columns(2)
        with col1:
            scenario_base = st.selectbox(
                "Base Scenario",
                options=scenarios,
                index=0,
                key="diff_base"
            )
        with col2:
            # Filter out the base scenario from comparison options
            comparison_options = [s for s in scenarios if s != scenario_base]
            if comparison_options:
                scenario_compare = st.selectbox(
                    "Compare To",
                    options=comparison_options,
                    index=0,
                    key="diff_compare"
                )
            else:
                st.warning("Select at least 2 different scenarios to compare")
                scenario_compare = None
        
        if scenario_compare:
            # Get matrices for both scenarios
            df_base = df[df['scenario'] == scenario_base].copy()
            df_base_no_total = df_base[df_base['home_district'] != 'Total']
            
            matrix_base = df_base_no_total.pivot_table(
                index='home_district',
                columns='work_district',
                values='abm_total_workers',
                aggfunc='sum',
                fill_value=0
            )
            
            df_comp = df[df['scenario'] == scenario_compare].copy()
            df_comp_no_total = df_comp[df_comp['home_district'] != 'Total']
            
            matrix_comp = df_comp_no_total.pivot_table(
                index='home_district',
                columns='work_district',
                values='abm_total_workers',
                aggfunc='sum',
                fill_value=0
            )
            
            # Ensure both matrices have the same structure
            all_rows = sorted(set(matrix_base.index) | set(matrix_comp.index))
            all_cols = sorted(set(matrix_base.columns) | set(matrix_comp.columns))
            
            matrix_base = matrix_base.reindex(index=all_rows, columns=all_cols, fill_value=0)
            matrix_comp = matrix_comp.reindex(index=all_rows, columns=all_cols, fill_value=0)
            
            # Display mode selector
            diff_mode = st.radio(
                "Difference Display",
                ["Absolute Difference", "Percentage Change"],
                horizontal=True,
                key="diff_mode"
            )
            
            # Calculate difference
            if diff_mode == "Absolute Difference":
                diff_matrix = matrix_comp - matrix_base
                # Add row and column totals
                diff_matrix['Total'] = diff_matrix.sum(axis=1)
                col_totals = diff_matrix.sum(axis=0)
                diff_matrix.loc['Total'] = col_totals
            else:  # Percentage Change
                # Calculate percentage change for each cell: (new - old) / old * 100
                with np.errstate(divide='ignore', invalid='ignore'):
                    diff_matrix = ((matrix_comp - matrix_base) / matrix_base.replace(0, np.nan)) * 100
                    diff_matrix = diff_matrix.fillna(0)
                
                # Calculate row totals correctly: (sum_new - sum_old) / sum_old * 100
                row_totals_base = matrix_base.sum(axis=1)
                row_totals_comp = matrix_comp.sum(axis=1)
                with np.errstate(divide='ignore', invalid='ignore'):
                    diff_matrix['Total'] = ((row_totals_comp - row_totals_base) / row_totals_base.replace(0, np.nan)) * 100
                    diff_matrix['Total'] = diff_matrix['Total'].fillna(0)
                
                # Calculate column totals correctly: (sum_new - sum_old) / sum_old * 100
                col_totals_base = matrix_base.sum(axis=0)
                col_totals_comp = matrix_comp.sum(axis=0)
                with np.errstate(divide='ignore', invalid='ignore'):
                    col_totals_pct = ((col_totals_comp - col_totals_base) / col_totals_base.replace(0, np.nan)) * 100
                    col_totals_pct = col_totals_pct.fillna(0)
                
                # Add the Total column to col_totals_pct for the grand total
                grand_total_base = matrix_base.sum().sum()
                grand_total_comp = matrix_comp.sum().sum()
                grand_total_pct = ((grand_total_comp - grand_total_base) / grand_total_base) * 100 if grand_total_base > 0 else 0
                col_totals_pct['Total'] = grand_total_pct
                
                diff_matrix.loc['Total'] = col_totals_pct
            
            # Display title
            st.markdown(f"**{scenario_compare}** minus **{scenario_base}** ({diff_mode})")
            st.caption("🟢 Positive values (increase) | 🔴 Negative values (decrease)")
            
            # Apply color styling
            def color_difference(val):
                """Apply color based on positive/negative values"""
                try:
                    if pd.isna(val) or val == 0:
                        color = 'black'
                    elif val > 0:
                        color = 'green'
                    else:
                        color = 'red'
                    return f'color: {color}'
                except:
                    return ''
            
            # Create styled dataframe
            styled_diff = diff_matrix.style.applymap(color_difference)
            
            # Format the numbers
            if diff_mode == "Absolute Difference":
                styled_diff = styled_diff.format("{:.0f}")
            else:  # Percentage Change
                styled_diff = styled_diff.format("{:.1f}%")
            
            # Display the difference matrix
            st.dataframe(
                styled_diff,
                use_container_width=True,
                height=400
            )
            
            # Summary statistics
            total_base_workers = int(matrix_base.sum().sum())
            total_comp_workers = int(matrix_comp.sum().sum())
            total_diff = total_comp_workers - total_base_workers
            pct_change = (total_diff / total_base_workers * 100) if total_base_workers > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(f"{scenario_base} Workers", f"{total_base_workers:,}")
            with col2:
                st.metric(f"{scenario_compare} Workers", f"{total_comp_workers:,}")
            with col3:
                st.metric("Difference", f"{total_diff:+,}", f"{pct_change:+.1f}%")

