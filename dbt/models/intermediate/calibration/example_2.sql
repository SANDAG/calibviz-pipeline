-- models/intermediate/int_trips_by_arrival_mode.sql
WITH base_data AS (
    SELECT * FROM {{ ref('stg_santrips') }}
),

-- Detailed level (non-employee) (e.g. res_nb, vis_nb, etc.)
detailed_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['arrival_mode', 'tour_type'],
        weight_column='trip',
        partition_column='tour_type',
        where_clause="tour_type != 'emp'"
    ) }}
),

-- General level (non-employee) (e.g. resident, visitor, etc.)
general_non_emp AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['arrival_mode', 'tour_type_general'],
        weight_column='trip',
        partition_column='tour_type_general',
        where_clause="tour_type != 'emp'"
    ) }}
),

-- Employee only (e.g. emp)
employee_only AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['arrival_mode', 'tour_type'],
        weight_column='trip',
        partition_column='tour_type',
        where_clause="tour_type = 'emp'"
    ) }}
),


totals AS (
    {{ aggregate_sum_percentages(
        source_table='base_data',
        dimension_columns=['arrival_mode'],
        weight_column='trip',
        where_clause="tour_type != 'emp'"
    ) }}
)

-- SELECT 'detailed' AS level, * FROM detailed_non_emp
-- UNION ALL
-- SELECT 'general' AS level, * FROM general_non_emp
-- UNION ALL
-- SELECT 'employee' AS level, * FROM employee_only


---- 


SELECT 
    'detailed' AS level,
    arrival_mode,
    tour_type,
    trip,
    percentage
FROM detailed_non_emp

UNION ALL

SELECT 
    'general' AS level,
    arrival_mode,
    tour_type_general AS tour_type,
    trip,
    percentage
FROM general_non_emp

UNION ALL

SELECT 
    'employee' AS level,
    arrival_mode,
    tour_type,
    trip,
    percentage
FROM employee_only

UNION ALL

SELECT 
    'total' AS level,
    arrival_mode,
    'Total' AS tour_type,
    trip,
    percentage
FROM totals