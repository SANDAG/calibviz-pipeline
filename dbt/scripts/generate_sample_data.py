import pandas as pd

# Define table names and their corresponding file names
TABLE_FILES = {
    'trips': 'final_trips.csv',
    'tours': 'final_tours.csv',
    'persons': 'final_persons.csv',
    'households': 'final_households.csv',
    'land_use': 'final_land_use.csv'
}

# Define dtypes for columns that are mostly nulls to prevent dtype inference warnings
DTYPES = {
    'trips': {
        'escort_participants': 'str',
        'school_escort_direction': 'str',
    },
    'tours': {
        'school_esc_outbound': 'str',
        'school_esc_inbound': 'str',
        'composition': 'str'
    }
}

# Define special read parameters for each table
READ_PARAMS = {
    'land_use': {
        'usecols': ['zone_id', 'mgra', 'pop', 'hhp', 'hh', 'hhs', 'emp_total', 'pseudomsa', 'exp_daily', 'TAZ']
    }
}


def load_and_create_sample_data(model_output_path, sample_size=12000):
    """
    Load model output CSV files and create sample datasets.

    Reads a sample of trips, then filters tours, persons, and households
    to maintain referential integrity. For land_use, reads only a subset of columns.

    Args:
        model_output_path: Directory path containing the model output files
        sample_size: Number of trips to include in sample (default 12000)

    Returns:
        dict: Dictionary with keys from TABLE_FILES containing filtered DataFrames
    """
    print("Reading model output files (first nrows of trips, full data for others)...")
    dfs = {}

    for table_name, filename in TABLE_FILES.items():
        read_params = {'dtype': DTYPES.get(table_name)}

        # Add sample size for trips only
        if table_name == 'trips':
            read_params['nrows'] = sample_size

        # Add special parameters if defined
        if table_name in READ_PARAMS:
            read_params.update(READ_PARAMS[table_name])

        dfs[table_name] = pd.read_csv(f'{model_output_path}\\{filename}', **read_params)
        print(f"  {table_name.replace('_', ' ').title()}: {len(dfs[table_name]):,}")

    print()

    # Filter related tables based on sampled trips
    tour_ids = dfs['trips']['tour_id'].unique()
    dfs['tours'] = dfs['tours'][dfs['tours']['tour_id'].isin(tour_ids)]

    person_ids = dfs['trips']['person_id'].unique()
    dfs['persons'] = dfs['persons'][dfs['persons']['person_id'].isin(person_ids)]

    household_ids = dfs['persons']['household_id'].unique()
    dfs['households'] = dfs['households'][dfs['households']['household_id'].isin(household_ids)]

    return dfs


def save_sample_data(dfs, output_path):
    """
    Write sample DataFrames to CSV files.

    Args:
        dfs: Dictionary containing DataFrames
        output_path: Directory path where sample files should be saved
    """
    print(f"Sample data saved to {output_path}")
    for table_name, df in dfs.items():
        output_file = f'{output_path}\\{TABLE_FILES[table_name]}'
        df.to_csv(output_file, index=False)
        print(f"  {table_name.replace('_', ' ').title()}: {len(df):,}")


# Main execution
if __name__ == "__main__":

    # Path to the ABM model output directory for the scenario of interest
    # Example:
    # r'T:\STORAGE-63T\2025RP_draft\abm_runs_v2\2022_S0_v2\output\resident'
    # REQUIRED: set this before running the script
    model_output_path = r''

    # Path where sample data will be saved
    # NOTE: Assumes script is run from dbt project root directory
    # This path should match the external_location defined in dbt's sources.yml
    sample_data_path = r'..\data\abm3'

    # Ensure the model output path has been provided
    if not model_output_path:
        raise ValueError(
            "model_output_path is not set. Please provide the path to the model output directory."
        )

    # Load and create sample data
    sample_data_dict = load_and_create_sample_data(model_output_path, sample_size=12000)

    # Save sample data to output directory
    save_sample_data(sample_data_dict, sample_data_path)