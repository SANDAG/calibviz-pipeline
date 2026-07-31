-- models/marts/fct_trips_comparison_person.sql
WITH arrival_modes AS (
    SELECT
        'arrival_mode' AS dimension,
        m.scenario,
        COALESCE(s.level, m.level) AS level,
        COALESCE(s.arrival_mode, m.arrival_mode) AS dimension_value,
        COALESCE(s.tour_type, m.tour_type) AS tour_type,
        s.trip AS survey_trip,
        s.percentage AS survey_percentage,
        m.trip AS model_trip,
        m.percentage AS model_percentage
    FROM {{ ref('int_trips_by_arrival_mode_survey_person') }} s
    FULL OUTER JOIN {{ ref('int_trips_by_arrival_mode_model_person') }} m
        ON s.level = m.level
        AND s.arrival_mode = m.arrival_mode
        AND s.tour_type = m.tour_type
),

origin_pmsas AS (
    SELECT
        'origin_pmsa' AS dimension,
        m.scenario,
        COALESCE(s.level, m.level) AS level,
        COALESCE(s.origin_pmsa, m.origin_pmsa) AS dimension_value,
        COALESCE(s.tour_type, m.tour_type) AS tour_type,
        s.trip AS survey_trip,
        s.percentage AS survey_percentage,
        m.trip AS model_trip,
        m.percentage AS model_percentage
    FROM {{ ref('int_trips_by_origin_pmsa_survey_person') }} s
    FULL OUTER JOIN {{ ref('int_trips_by_origin_pmsa_model_person') }} m
        ON s.level = m.level
        AND s.origin_pmsa = m.origin_pmsa
        AND s.tour_type = m.tour_type
)

SELECT
    dimension,
    scenario,
    level,
    dimension_value,
    tour_type,
    survey_trip,
    survey_percentage,
    model_trip,
    model_percentage,
    model_percentage - survey_percentage AS percentage_diff
FROM arrival_modes

UNION ALL

SELECT
    dimension,
    scenario,
    level,
    dimension_value,
    tour_type,
    survey_trip,
    survey_percentage,
    model_trip,
    model_percentage,
    model_percentage - survey_percentage AS percentage_diff
FROM origin_pmsas
