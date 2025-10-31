# calibviz-pipeline
A lightweight data pipeline and visualization project using DBT for data transformations and Streamlit for interactive calibration dashboards.

The project is designed to run locally with DuckDB as the database engine.

📋 Requirements

Before getting started, make sure you have the following installed:

Python 3.10+

uv
 (Python package and environment manager)

Visual Studio Code (recommended for development)
Optional:

DBCode VS Code Extension
 – for enhanced SQL and DuckDB integration

# CalibViz Setup Guide

## Initial Setup

### 1. Clone and Setup Environment
```bash
# Clone the repository in Visual Studio Code
# File > Open Folder > Select your project directory

# Create virtual environment
uv venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
uv sync
```

### 2. Configure dbt
```bash
# Navigate to dbt directory
cd dbt

# Initialize dbt project
dbt init --profiles-dir .
```

When prompted:
- Select `1` for DuckDB

### 3. Configure Database Connection

Edit `profiles.yml` in dbt folder.
Change the dev targets:
```yaml
    dev:
      type: duckdb
      path: ../resident_calibration.duckdb
      threads: 20 # Increase thread count for better performance 
```

### 4. Build dbt Models
```bash
# Build all models
dbt build

# Other options:
  # Build specific model (if needed)
  dbt build --select household_size

  # Build metrics and dependencies
  dbt build --select metrics+
```

## Running the Streamlit Application

### 1. Configure Streamlit
```bash
# Navigate to streamlit directory
cd ../streamlit

```

### 2. Launch Application
```bash
streamlit run app.py
```

## Documentation

### Generate and View dbt Documentation
```bash
# Navigate to dbt directory
cd ../dbt

# Generate documentation
dbt docs generate

# Serve documentation (opens in browser)
dbt docs serve
```

## Project Structure
```
project/
├── dbt/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── _sources.yml
│   │   │   ├── abm3_output/
│   │   │   └── household_travel_survey/
│   │   └── metrics/
│   │       ├── household_metrics/
│   │       ├── persons_metrics/
│   │       └── trip_metrics/
│   └── dbt_project.yml
├── streamlit/
│   ├── app.py
│   └── pages/
├── resident_calibration.duckdb
└── .venv/
```
