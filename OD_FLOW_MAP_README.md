# OD Flow Map Feature

## Overview

This improvement adds **interactive Origin-Destination (OD) flow mapping** capabilities to the calibration dashboard, implementing one of the key features from the ABM-Replica comparison plan. The feature visualizes trip flows between Traffic Analysis Zones (TAZs) using PyDeck's GPU-accelerated arc layers.

## What's New

### 1. **Geographic Visualization with PyDeck**
- Interactive 3D arc map showing trip flows between TAZ pairs
- Arc width and color represent trip volumes
- Hover tooltips display detailed flow information
- Red dots mark TAZ centroids on the map

### 2. **DBT Model for OD Aggregation** 
Model: `dbt/models/metrics/resident/trip_metrics/od_flow_map.sql`

Aggregates trip data:
- Groups trips by origin TAZ, destination TAZ, mode, and time period
- Joins with TAZ geography (centroids) for mapping
- Calculates trip counts, distances, and travel times
- Filters out intra-zonal trips for cleaner visualization

### 3. **Interactive Filters**
Users can filter the map by:
- **Trip Mode**: Select specific modes (drive alone, shared ride, transit, etc.)
- **Time Period**: Filter by EA/AM/MD/PM/EV time periods
- **Minimum Trip Volume**: Show only significant flows
- **Top N Flows**: Limit display for better performance

### 4. **TAZ Geography Seed Data**
File: `dbt/seeds/geo/taz_centroids.csv`

Sample TAZ centroids with longitude/latitude coordinates. Replace with actual SANDAG TAZ geography for production use.

## Setup Instructions

### 1. Install Dependencies

```bash
# Activate virtual environment
.venv\Scripts\activate

# Install new pydeck dependency
uv sync
```

### 2. Load Geography Seed Data

```bash
cd dbt

# Load TAZ centroids
dbt seed --select taz_centroids
```

**Important**: The provided `taz_centroids.csv` contains sample coordinates. For production:
- Replace with actual SANDAG TAZ centroids
- Ensure all TAZ IDs from your ABM output are included
- Coordinates should be in WGS84 (longitude, latitude)

### 3. Run DBT Model

```bash
# Run the OD flow aggregation model
dbt run --select od_flow_map

# Or run all trip metrics
dbt run --select +metrics.resident.trip_metrics+
```

### 4. Launch Dashboard

```bash
cd ../streamlit
streamlit run app.py
```

Navigate to: **Resident - Trip Metrics → OD Flow Map**

## Usage Guide

### Map Interaction
- **Hover** over arcs to see flow details (origin, destination, trip count, distance, time)
- **Hover** over red dots to see TAZ information
- **Scroll** to zoom in/out
- **Click and drag** to pan the map
- **Ctrl + drag** to rotate the map

### Filters Panel
Located in the left sidebar:

1. **Trip Mode**: Multi select specific travel modes
   - Filters available modes from the data
   - Defaults to first 3 modes
   
2. **Time Period**: Select EA/AM/MD/PM/EV periods
   - Shows only periods with data
   - Defaults to all periods
   
3. **Minimum Trip Volume**: Slider to filter small flows
   - Hides flows below the threshold
   - Helps focus on major corridors
   
4. **Show Top N Flows**: Limits display for performance
   - Range: 10-500 flows
   - Default: 100
   - Sorted by trip volume

### Data Table
Expand the "View Flow Data Table" section to:
- See detailed tabular data for displayed flows
- Sort and search through records
- Download filtered data as CSV

## Technical Details

### Data Flow
```
ABM Trips (final_trips.csv)
    ↓
stg_abm3_trips (DBT staging)
    ↓
od_flow_map (DBT model)
    ↓ (aggregates by OD pair + mode + period)
    ↓ (joins with TAZ centroids)
    ↓
Streamlit Page (od_flow_map.py)
    ↓
PyDeck Arc Visualization
```

### Performance Optimization
- **Caching**: Streamlit caches data for 10 minutes (`@st.cache_data`)
- **Pre-aggregation**: DBT model aggregates trips before visualization
- **Top N limiting**: Default 100 flows prevents performance issues
- **Minimum threshold**: Filters out insignificant flows (< 0.1 trips)

### PyDeck Layers
1. **ArcLayer**: Shows trip flows as curved arcs
   - Source: Blue (origin TAZ)
   - Target: Orange (destination TAZ)
   - Width: Scaled by trip volume (1-10 pixels)
   
2. **ScatterplotLayer**: Shows TAZ centroids
   - Red circles marking zone centers
   - 200m radius (map units)

## Comparison to Plan

This implementation aligns with the ABM-Replica Dashboard plan:

✅ **Implemented from Plan:**
- PyDeck for OD flow visualization (Step 6)
- DBT transformation models for OD aggregation (Step 2)
- Interactive filters in Streamlit sidebar (Step 5)
- Mode and time period filtering (Step 5)
- Performance optimization with pre-aggregation (Step 2)

📋 **Adapted for Current Setup:**
- Uses DuckDB instead of PostgreSQL (existing infrastructure)
- Compares ABM with HTS data (not Replica yet)
- Sample TAZ geography (replace with SANDAG shapefile centroids)

🔮 **Future Enhancements:**
- Add actual Replica data integration (Step 4 from plan)
- Calculate OD flow differences (ABM vs Replica/HTS)
- Add RMSE and correlation metrics
- City-level aggregation option
- Export to PDF/PowerPoint for reports

## Troubleshooting

### "No OD flow data found"
**Solution**: Run the DBT model
```bash
cd dbt
dbt run --select od_flow_map
```

### "No modes/periods available"
**Solution**: Check that your ABM data has populated these fields
```sql
-- Test query
SELECT DISTINCT trip_mode, trip_period 
FROM staging.stg_abm3_trips 
WHERE trip_mode IS NOT NULL;
```

### TAZ coordinates not showing
**Solution**: Verify TAZ centroids seed data is loaded
```bash
dbt seed --select taz_centroids
```

Check that TAZ IDs in your trip data match the seed file

### Performance issues / slow loading
**Solutions**:
- Reduce "Top N Flows" slider (try 50 instead of 100)
- Increase "Minimum Trip Volume" threshold
- Select fewer modes / time periods

## File Structure
```
├── dbt/
│   ├── models/
│   │   └── metrics/
│   │       └── resident/
│   │           └── trip_metrics/
│   │               └── od_flow_map.sql          # OD aggregation model
│   └── seeds/
│       └── geo/
│           └── taz_centroids.csv                # TAZ geography
│
├── streamlit/
│   ├── app.py                                    # Updated navigation
│   └── pages/
│       └── resident/
│           └── trip_metrics/
│               └── od_flow_map.py               # PyDeck visualization
│
├── pyproject.toml                                # Added pydeck dependency
└── OD_FLOW_MAP_README.md                        # This file
```

## Next Steps

1. **Replace Sample Geography**: Update `taz_centroids.csv` with actual SANDAG TAZ centroids
   - Extract from TAZ shapefile
   - Calculate centroids using QGIS or GeoPandas
   - Ensure WGS84 coordinates (EPSG:4326)

2. **Add Replica Data** (if available):
   - Create staging model for Replica OD flows
   - Join with ABM flows for comparison
   - Add difference calculations (ABM - Replica)
   - Color arcs by difference magnitude

3. **Enhance Visualization**:
   - Add basemap layer with city boundaries
   - Implement corridor selection (click to highlight)
   - Add animation for time period progression
   - Include mode share pie charts for selected corridors

4. **Metrics Dashboard**:
   - Calculate RMSE, MAPE for OD flows
   - Show correlation scatter plots
   - Identify top discrepancies for calibration focus

## References

- [PyDeck Documentation](https://deckgl.readthedocs.io/en/latest/)
- [Streamlit PyDeck Integration](https://docs.streamlit.io/develop/api-reference/charts/st.pydeck_chart)
- Original Plan: `plan-abmReplicaDashboard.prompt.md`
