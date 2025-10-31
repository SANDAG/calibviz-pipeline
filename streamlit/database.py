"""
database.py - Shared database connection and query utilities for CalibViz Pipeline

This module provides cached database connections and common query functions
that can be imported and used across all pages in the Streamlit app.
"""

import streamlit as st
import duckdb
import time
from typing import Tuple, Optional
import pandas as pd


@st.cache_resource
def get_db_connection() -> Tuple[Optional[duckdb.DuckDBPyConnection], float]:
    """
    Establish and cache the database connection.
    
    Returns:
        Tuple of (connection object, elapsed time in seconds)
        Returns (None, 0) if connection fails
    """
    try:
        start = time.time()
        conn = duckdb.connect('../resident_calibration.duckdb', read_only=True)
        elapsed = time.time() - start
        return conn
    except Exception as e:
        st.error(f"❌ Failed to connect to database: {e}")
        return None


@st.cache_data(ttl=600)  # Cache for 10 minutes
def query_household_size(_conn: duckdb.DuckDBPyConnection) -> Tuple[Optional[pd.DataFrame], float]:
    """
    Query household size data with timing.
    
    Args:
        _conn: DuckDB connection object (prefixed with _ to prevent hashing)
    
    Returns:
        Tuple of (DataFrame with results, elapsed time in seconds)
        Returns (None, 0) if query fails
    """
    if _conn is None:
        return None, 0
    
    try:
        start = time.time()
        query = "SELECT hhsize, abm_percentage, hts_percentage FROM main_metrics.hhsize"
        result = _conn.execute(query).fetch_df()
        elapsed = time.time() - start
        return result
    except Exception as e:
        st.error(f"❌ Query failed: {e}")
        return None


@st.cache_data(ttl=600)
def query_all_tables(_conn: duckdb.DuckDBPyConnection) -> Optional[pd.DataFrame]:
    """
    Get list of all tables in the database.
    
    Args:
        _conn: DuckDB connection object
    
    Returns:
        DataFrame with table information or None if query fails
    """
    if _conn is None:
        return None
    
    try:
        query = """
        SELECT 
            table_schema,
            table_name,
            table_type
        FROM information_schema.tables
        WHERE table_schema = 'main'
        ORDER BY table_name
        """
        return _conn.execute(query).fetch_df()
    except Exception as e:
        st.error(f"❌ Failed to fetch table list: {e}")
        return None


@st.cache_data(ttl=600)
def query_table_info(_conn: duckdb.DuckDBPyConnection, table_name: str) -> Optional[pd.DataFrame]:
    """
    Get column information for a specific table.
    
    Args:
        _conn: DuckDB connection object
        table_name: Name of the table to describe
    
    Returns:
        DataFrame with column information or None if query fails
    """
    if _conn is None:
        return None
    
    try:
        query = f"DESCRIBE main_staging.{table_name}"
        return _conn.execute(query).fetch_df()
    except Exception as e:
        st.error(f"❌ Failed to describe table '{table_name}': {e}")
        return None


@st.cache_data(ttl=600)
def execute_custom_query(_conn: duckdb.DuckDBPyConnection, query: str) -> Tuple[Optional[pd.DataFrame], float]:
    """
    Execute a custom SQL query with timing.
    
    Args:
        _conn: DuckDB connection object
        query: SQL query string to execute
    
    Returns:
        Tuple of (DataFrame with results, elapsed time in seconds)
        Returns (None, 0) if query fails
    """
    if _conn is None:
        return None, 0
    
    try:
        start = time.time()
        result = _conn.execute(query).fetch_df()
        elapsed = time.time() - start
        return result, elapsed
    except Exception as e:
        st.error(f"❌ Custom query failed: {e}")
        return None, 0


@st.cache_data(ttl=600)
def get_table_row_count(_conn: duckdb.DuckDBPyConnection, table_name: str) -> Optional[int]:
    """
    Get the number of rows in a table.
    
    Args:
        _conn: DuckDB connection object
        table_name: Name of the table
    
    Returns:
        Number of rows or None if query fails
    """
    if _conn is None:
        return None
    
    try:
        query = f"SELECT COUNT(*) as count FROM main_staging.{table_name}"
        result = _conn.execute(query).fetch_df()
        return result['count'][0]
    except Exception as e:
        st.error(f"❌ Failed to count rows in '{table_name}': {e}")
        return None


def clear_cache():
    """Clear all cached data and force refresh."""
    st.cache_data.clear()
    st.success("✅ Cache cleared successfully!")


def display_connection_status():
    """Display connection status in the sidebar."""
    conn = get_db_connection()
    
    with st.sidebar:
        st.markdown("### 🔌 Database Status")
        if conn is not None:
            st.success("✅ Connected")
            #st.caption(f"Connection: {conn_time:.3f}s")
            
            # Display database path
            st.caption("**Path:** `../resident_calibration.duckdb`")
            
            # Add refresh button
            if st.button("🔄 Refresh Data", use_container_width=True):
                clear_cache()
                st.rerun()
        else:
            st.error("❌ Disconnected")
            st.caption("Check database path and permissions")


def get_database_stats(_conn: duckdb.DuckDBPyConnection) -> dict:
    """
    Get general database statistics.
    
    Args:
        _conn: DuckDB connection object
    
    Returns:
        Dictionary with database statistics
    """
    if _conn is None:
        return {}
    
    stats = {}
    
    try:
        # Get total tables
        tables = query_all_tables(_conn)
        stats['total_tables'] = len(tables) if tables is not None else 0
        
        # Get household size stats
        hhsize_df = query_household_size(_conn)
        if hhsize_df is not None:
            stats['total_household_records'] = len(hhsize_df)
            stats['avg_abm3_percentage'] = hhsize_df['abm3_percentage'].mean()
            stats['avg_hts_percentage'] = hhsize_df['hts_percentage'].mean()
    except Exception as e:
        st.warning(f"⚠️ Could not fetch all database stats: {e}")
    
    return stats


# Example usage in other files:
"""
from database import get_db_connection, query_household_size, display_connection_status

# In your page:
display_connection_status()  # Show connection status in sidebar
conn, _ = get_db_connection()
df, query_time = query_household_size(conn)

# Use df for your visualizations...
"""