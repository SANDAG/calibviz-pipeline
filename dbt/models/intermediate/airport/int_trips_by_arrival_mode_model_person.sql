-- models/intermediate/int_trips_by_arrival_mode_person.sql
WITH base_data AS (
    SELECT * FROM {{ ref('stg_tripcount_mode') }}
),

-- Detailed level (non-employee) (e.g. res_nb, vis_nb, etc.)
detailed_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['scenario', 'arrival_mode', 'tour_type'],
        weight_column='person_trip',
        partition_column='scenario, tour_type',
        where_clause="tour_type != 'emp' AND tour_type != 'external'"
    ) }}
),

-- General level (non-employee) (e.g. resident, visitor, etc.)
general_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['scenario', 'arrival_mode', 'tour_type_general'],
        weight_column='person_trip',
        partition_column='scenario, tour_type_general',
        where_clause="tour_type != 'emp'"
    ) }}
),

-- Employee only (e.g. emp)
employee_only AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['scenario', 'arrival_mode', 'tour_type'],
        weight_column='person_trip',
        partition_column='scenario, tour_type',
        where_clause="tour_type = 'emp'"
    ) }}
),

combined as (
    SELECT 
    'detailed' AS level,
    scenario,
    arrival_mode,
    tour_type,
    person_trip as trip,
    percentage
FROM detailed_non_emp

UNION ALL

SELECT 
    'general' AS level,
    scenario,
    arrival_mode,
    tour_type_general AS tour_type,
    person_trip as trip,
    percentage
FROM general_non_emp

UNION ALL

SELECT 
    'employee' AS level,
    scenario,
    arrival_mode,
    tour_type,
    person_trip as trip,
    percentage
FROM employee_only
),

tour_type_totals AS (
    {{ aggregate_sum_percentages(
        source_table='combined',
        dimension_columns=['scenario', 'tour_type'],
        weight_column='trip',
        partition_column='scenario',
        where_clause="tour_type != 'emp'"
    ) }}
),

arrival_mode_totals AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['scenario', 'arrival_mode'],
        weight_column='person_trip',
        partition_column='scenario',
        where_clause="tour_type != 'emp'"
    ) }}
)

SELECT * FROM combined

UNION ALL

SELECT 
    'total' AS level,
    scenario,
    arrival_mode,
    'total' as tour_type,
    person_trip as trip,
    percentage
FROM arrival_mode_totals

UNION ALL

SELECT 
    'total' AS level,
    scenario,
    'total' as arrival_mode,
    tour_type,
    trip,
    percentage
FROM tour_type_totals
