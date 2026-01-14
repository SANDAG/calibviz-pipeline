import pandas as pd

def load_model_outputs(model_output_path, sample_size=12000):
    """
    Load model output CSV files with appropriate data types.
    
    Reads a sample of trips and full datasets for tours, persons, households and land_use.
    
    Args:
        model_output_path: Directory path containing the model output files
        sample_size: Number of trips to include in sample (default 12000)
        
    Returns:
        tuple: (sample_trips, tours, persons, households, land_use) DataFrames
    """
    # Define dtypes for columns that are mostly nulls to prevent dtype inference warnings
    trips_dtypes = {
        'escort_participants': 'str',
        'school_escort_direction': 'str',
    }
    tours_dtypes = {
        'school_esc_outbound': 'str',
        'school_esc_inbound': 'str',
        'composition': 'str'
    }
    
    # Read only the first N trips to create sample (avoids loading entire 10M+ row file)
    print("Reading model output files...") 
    sample_trips = pd.read_csv(
        f'{model_output_path}\\final_trips.csv',
        dtype=trips_dtypes,
        nrows=sample_size
    )
    print(f"  Trip Sample: {len(sample_trips):,}")

    # Load full tours, persons, households, and land use files
    tours = pd.read_csv(f'{model_output_path}\\final_tours.csv', dtype=tours_dtypes)
    print(f"  Tours: {len(tours):,}")
    persons = pd.read_csv(f'{model_output_path}\\final_persons.csv')
    print(f"  Persons: {len(persons):,}")
    households = pd.read_csv(f'{model_output_path}\\final_households.csv')
    print(f"  Households: {len(households):,}")
    land_use = pd.read_csv(f'{model_output_path}\\final_land_use.csv')
    print(f"  Land Use: {len(land_use):,}\n")
    
    return sample_trips, tours, persons, households, land_use


def create_sample_data(sample_trips, tours, persons, households):
    """
    Create sample datasets by filtering related records based on trip sample.
    
    From the first N trips, finds all related tours, persons, and households
    to maintain referential integrity across tables.
    
    Args:
        sample_trips: first N rows of trips DataFrame
        tours: Full tours DataFrame
        persons: Full persons DataFrame
        households: Full households DataFrame
        
    Returns:
        tuple: (sample_tours, sample_persons, sample_households) DataFrames
    """

    # Get all tours associated with sampled trips
    tour_ids = sample_trips['tour_id'].unique()
    sample_tours = tours[tours['tour_id'].isin(tour_ids)]
    
    # Get all persons associated with sampled trips
    person_ids = sample_trips['person_id'].unique()
    sample_persons = persons[persons['person_id'].isin(person_ids)]
    
    # Get all households associated with sampled persons
    household_ids = sample_persons['household_id'].unique()
    sample_households = households[households['household_id'].isin(household_ids)]
    
    return sample_tours, sample_persons, sample_households


def save_sample_data(sample_trips, sample_tours, sample_persons, sample_households, land_use, output_path):
    """
    Write sample DataFrames to CSV files. For land_use use full dataset.
    
    Args:
        sample_trips: Sample trips DataFrame
        sample_tours: Sample tours DataFrame
        sample_persons: Sample persons DataFrame
        sample_households: Sample households DataFrame
        land_use: full land use DataFrame
        output_path: Directory path where sample files should be saved
    """
    sample_trips.to_csv(f'{output_path}\\final_trips.csv', index=False)
    sample_tours.to_csv(f'{output_path}\\final_tours.csv', index=False)
    sample_persons.to_csv(f'{output_path}\\final_persons.csv', index=False)
    sample_households.to_csv(f'{output_path}\\final_households.csv', index=False)
    land_use.to_csv(f'{output_path}\\final_land_use.csv', index=False)
    
    print(f"Sample data saved to {output_path}")
    print(f"  Trips: {len(sample_trips):,}")
    print(f"  Tours: {len(sample_tours):,}")
    print(f"  Persons: {len(sample_persons):,}")
    print(f"  Households: {len(sample_households):,}")
    print(f"  Land Use: {len(land_use):,}")


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

    # Load model outputs (sample of trips, full tours/persons/households/land_use)
    sample_trips, tours, persons, households, land_use = load_model_outputs(
        model_output_path, sample_size=12000
    )

    # Create sample data (filter tours/persons/households based on sample trips)
    sample_tours, sample_persons, sample_households = create_sample_data(
        sample_trips, tours, persons, households
    )
    
    # Save sample data to test directory
    save_sample_data(sample_trips, sample_tours, sample_persons, sample_households, land_use, sample_data_path)
