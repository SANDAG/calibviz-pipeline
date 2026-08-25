"""
scenario_config.py - Shared scenario selection utilities for CalibViz Pipeline

This module provides reusable components for scenario and survey year selection
that can be imported and used across all resident pages in the Streamlit app.
"""

import streamlit as st
import yaml
from pathlib import Path
from typing import List, Tuple


@st.cache_data
def load_resident_scenarios() -> List[str]:
    """
    Load resident scenarios from dbt_project.yml.
    
    Returns:
        List of scenario names configured in dbt_project.yml
    """
    dbt_project_path = Path(__file__).parent.parent / "dbt" / "dbt_project.yml"
    with open(dbt_project_path, 'r') as f:
        dbt_config = yaml.safe_load(f)
        return dbt_config.get('vars', {}).get('resident_scenarios', [])


def render_scenario_selector(
    label: str = "### Select ABM Scenario(s)",
    default_all: bool = False,
    single_select: bool = False
) -> List[str]:
    """
    Render a scenario selector widget.
    
    Args:
        label: The label to display above the selector
        default_all: If True, select all scenarios by default; if False, select only the first
        single_select: If True, use selectbox (single selection); if False, use multiselect
    
    Returns:
        List of selected scenario names (or single-item list if single_select=True)
    """
    scenarios_list = load_resident_scenarios()
    
    if not scenarios_list:
        st.error("No resident scenarios found in dbt_project.yml")
        st.stop()
    
    st.markdown(label)
    
    if single_select:
        # Single scenario selection using selectbox
        selected = st.selectbox(
            "Scenario",
            options=scenarios_list,
            index=0,
            label_visibility="collapsed"
        )
        return [selected]
    else:
        # Multiple scenario selection using multiselect
        default_selection = scenarios_list if default_all else [scenarios_list[0]]
        
        selected = st.multiselect(
            "Scenarios",
            options=scenarios_list,
            default=default_selection,
            label_visibility="collapsed"
        )
        
        if not selected:
            st.warning("Please select at least one scenario")
            st.stop()
        
        return selected


def render_survey_year_selector(
    label: str = "### Select Survey Year(s)",
    default_years: List[str] = None,
    single_select: bool = False
) -> List[str]:
    """
    Render a survey year selector widget.
    
    Args:
        label: The label to display above the selector
        default_years: List of years to select by default (defaults to ["2022"])
        single_select: If True, use selectbox (single selection); if False, use multiselect
    
    Returns:
        List of selected survey years (or single-item list if single_select=True)
    """
    if default_years is None:
        default_years = ["2022"]
    
    available_years = ["2022", "2023"]
    
    st.markdown(label)
    
    if single_select:
        # Single year selection using selectbox
        default_index = available_years.index(default_years[0]) if default_years else 0
        selected = st.selectbox(
            "Survey Year",
            options=available_years,
            index=default_index,
            label_visibility="collapsed"
        )
        return [selected]
    else:
        # Multiple year selection using multiselect
        selected = st.multiselect(
            "Survey Years",
            options=available_years,
            default=default_years,
            label_visibility="collapsed"
        )
        
        if not selected:
            st.warning("Please select at least one survey year")
            st.stop()
        
        return selected


def format_scenario_sql_list(scenarios: List[str]) -> str:
    """
    Format a list of scenarios for use in SQL IN clause.
    
    Args:
        scenarios: List of scenario names
    
    Returns:
        Formatted string like "'scenario1', 'scenario2', 'scenario3'"
    """
    return "', '".join(scenarios)


def get_scenario_config() -> Tuple[List[str], List[str]]:
    """
    Convenience function to get both scenario and survey year selections.
    
    Returns:
        Tuple of (selected_scenarios, selected_survey_years)
    """
    scenarios = render_scenario_selector()
    survey_years = render_survey_year_selector()
    return scenarios, survey_years
