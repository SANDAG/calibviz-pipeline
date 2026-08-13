-- models/intermediate/int_trips_by_origin_pmsa_survey_person.sql
WITH base_data AS (
    SELECT * FROM {{ ref('stg_departing_trips_mode_person') }}
),

-- Detailed level (non-employee) (e.g. res_nb, vis_nb, etc.)
detailed_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['origin_pmsa', 'tour_type'],
        weight_column='trip',
        partition_column='tour_type',
        where_clause="tour_type != 'emp' AND tour_type != 'external'"
    ) }}
),

-- General level (non-employee) (e.g. resident, visitor, etc.)
general_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['origin_pmsa', 'tour_type_general'],
        weight_column='trip',
        partition_column='tour_type_general',
        where_clause="tour_type != 'emp'"
    ) }}
),

-- Employee only (e.g. emp)
employee_only AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['origin_pmsa', 'tour_type'],
        weight_column='trip',
        partition_column='tour_type',
        where_clause="tour_type = 'emp'"
    ) }}
),

combined as (
    SELECT 
    'detailed' AS level,
    origin_pmsa,
    tour_type,
    trip,
    percentage
FROM detailed_non_emp

UNION ALL

SELECT 
    'general' AS level,
    origin_pmsa,
    tour_type_general AS tour_type,
    trip,
    percentage
FROM general_non_emp

UNION ALL

SELECT 
    'employee' AS level,
    origin_pmsa,
    tour_type,
    trip,
    percentage
FROM employee_only
),

tour_type_totals AS (
    {{ aggregate_sum_percentages(
        source_table='combined',
        dimension_columns=['tour_type'],
        weight_column='trip',
        where_clause="tour_type != 'emp'"
    ) }}
),

origin_pmsa_totals AS (
    {{ aggregate_sum_percentages(
        source_table='combined',
        dimension_columns=['origin_pmsa'],
        weight_column='trip',
        where_clause="tour_type != 'emp'"
    ) }}
)

SELECT * FROM combined

UNION ALL

SELECT 
    'total' AS level,
    origin_pmsa,
    'total' as tour_type,
    trip,
    percentage
FROM origin_pmsa_totals

UNION ALL

SELECT 
    'total' AS level,
    'total' as origin_pmsa,
    tour_type,
    trip,
    percentage
FROM tour_type_totals
