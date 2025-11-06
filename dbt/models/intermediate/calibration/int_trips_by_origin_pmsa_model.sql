-- models/intermediate/int_trips_by_origin_pmsa_results.sql
WITH base_data AS (
    SELECT * FROM {{ ref('stg_tripcount_mode') }}
    --WHERE scenario_id IN ({{ var('calibration_scenario_id') }}) AND model in ({{ var('calibration_model') }})
),

-- Detailed level (non-employee) (e.g. res_nb, vis_nb, etc.)
detailed_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['origin_pmsa', 'tour_type'],
        weight_column='trip',
        partition_column='tour_type',
        where_clause="tour_type != 'emp'"
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

general_totals AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['tour_type_general'],
        weight_column='trip',
        partition_column=None,
        where_clause="tour_type != 'emp'"
    ) }}
)






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

UNION ALL

SELECT
    'total' AS level,
    'total' as origin_pmsa,
    tour_type_general AS tour_type,
    trip,
    percentage
FROM general_totals
