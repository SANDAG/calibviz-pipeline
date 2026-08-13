# calibviz-pipeline
A lightweight data pipeline and visualization project using DBT for data transformations and Streamlit for interactive calibration dashboards.

The project is designed to run locally with DuckDB as the database engine.

📋 Requirements

Before getting started, make sure you have the following installed:

- Python 3.10+
- uv (Python package and environment manager)
- Visual Studio Code (recommended for development)

**Optional:**
for enhanced SQL and DuckDB integration
- DBCode VS Code Extension  
- DBeaver

---

# 🚀 Quick Start (After Initial Setup)

If the initial setup is completed, follow these steps to run the resident calibration visualizer pipeline:
```bash
# 1. Activate virtual environment
.venv\Scripts\activate

# 2. Navigate to dbt directory
cd dbt

# 3. Load csv files, e.g., mode mapping (only need to run once or when seed data changes)
dbt seed

# 4. Run resident metrics model only
dbt run --select +metrics.resident+

# 5. (Optional) Launch Streamlit dashboard
cd ../streamlit
streamlit run app.py
```

---

# 📦 Initial Setup (One-Time Only)

Complete these steps only once when first setting up the project.

## 1. Clone and Setup Environment
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

## 2. Configure dbt
```bash
# Navigate to dbt directory
cd dbt

# Initialize dbt project
dbt init --profiles-dir .
```

When prompted:
- Select `1` for DuckDB

## 3. Configure Database Connection

Edit `profiles.yml` in the dbt folder.
Change the dev target:
```yaml
    dev:
      type: duckdb
      path: ../resident_calibration.duckdb
      threads: 20 # Increase thread count for better performance 
``` 

---

# 💻 Usage

## Running the Data Pipeline
```bash
# 1. Activate environment (if not already active)
.venv\Scripts\activate

# 2. Navigate to dbt folder
cd dbt

# 3. Run resident metrics
dbt run --select +metrics.resident+

**⚠️ Important:** The airport model requires a connection string that is not configured by default. 
```

**Other useful dbt commands:**
```bash
# Build specific model
dbt run --select household_size

# Build specific model & all the upstream dependenies
dbt run --select +household_size
```

## Running the Streamlit Application
```bash
# Navigate to streamlit directory
cd streamlit

# Launch application
streamlit run app.py
```

---
# 📁 Project Structure
```
calibviz-pipeline/
├── dbt/                          # DBT transformations
│   ├── models/
│   │   ├── staging/              # Raw data sources
│   │   │   ├── _sources.yml      # Data source definitions
│   │   │   ├── abm3_output/
│   │   │   └── household_travel_survey/
│   │   ├── intermediate/         # Intermediate transformations
│   │   └── metrics/              # Aggregated metrics
│   │       ├── resident/         
│   │       └── airport/          
│   ├── macros/                   # Reusable SQL functions
│   ├── seeds/                    # Static CSV data, e.g mode mapping
│   ├── dbt_project.yml           # Project configuration
│   └── profiles.yml              # Database configuration
│
├── streamlit/                    # Dashboard application
│   ├── app.py
│   └── pages/
│
├── data/                         # Sample data
├── resident_calibration.duckdb   # DuckDB database
├── pyproject.toml                # Dependencies
└── .venv/                        # Virtual environment
```
---
# 📚 Documentation

See [dbt/README.md](dbt/README.md) for more details on running dbt models and available configuration (e.g. group quarters inclusion).

### Generate and View dbt Documentation
```bash
# Navigate to dbt directory
cd dbt

# Generate documentation
dbt docs generate

# Serve documentation (opens in browser)
dbt docs serve
```

---
