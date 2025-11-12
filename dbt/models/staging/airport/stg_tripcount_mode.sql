{{ config(
    materialized='table'
) }}

with trip_source as (
    SELECT * EXCLUDE (origin),
           origin as origin_mgra 
    FROM {{ source('abm3_airport_output', 'final_santrips') }}
),

tour_source as (
    SELECT tour_id, tour_type 
    FROM {{ source('abm3_airport_output', 'final_santours') }}
),

mgra_taz_pmsa_xref as (
    SELECT 
    TAZ as taz,
    MGRA as mgra,
    PSEUDOMSA as origin_pmsa
    FROM {{ ref('mgra_taz_pmsa_xref') }}
),

trip_joined_xref as (
    SELECT
        ts.*,
        xref.origin_pmsa
    FROM trip_source ts
    LEFT JOIN mgra_taz_pmsa_xref xref 
        ON ts.origin_mgra = xref.mgra
)

SELECT
    origin_mgra,
    origin_pmsa::INTEGER::VARCHAR as origin_pmsa,
    CASE WHEN arrival_mode = 'TAXI_LOC1' THEN 'TAXI'
         WHEN arrival_mode = 'RIDEHAIL_LOC1' AND trip_mode = 'SHARED2' THEN 'TNC_SINGLE'
         WHEN arrival_mode = 'RIDEHAIL_LOC1' AND trip_mode = 'SHARED3' THEN 'TNC_SHARED'
         ELSE trip_mode
    END AS
    trip_mode,
    CASE WHEN tour_type LIKE 'emp' THEN 'emp'
         WHEN tour_type LIKE 'res_per%' THEN 'res_nb'
         WHEN tour_type LIKE 'res_bus%' THEN 'res_bus'
         WHEN tour_type LIKE 'vis_per%' THEN 'vis_nb'
         WHEN tour_type LIKE 'vis_bus%' THEN 'vis_bus'
         ELSE tour_type
    END AS tour_type,
    case 
        when tour_type like 'res_%' then 'resident'
        when tour_type like 'vis_%' then 'visitor'
        when tour_type like 'emp%' then 'employee'
        else tour_type
    end as tour_type_general,
    outbound,
    -- mode mapping
    -- amts.mapped_value as arrival_mode,
    COALESCE(m.final_mode, trip_joined_xref.arrival_mode) as arrival_mode,
    weight_person_trip as trip
FROM trip_joined_xref
JOIN tour_source ts USING (tour_id)
LEFT JOIN {{ ref('arrival_mode_mapping') }} m ON m.original_mode = trip_joined_xref.arrival_mode
-- JOIN {{ ref('arrival_mode_to_survey') }} amts USING (arrival_mode)
---JOIN {{ ref ('arrival_mode_mapping')}} m USING (arrival_mode)
WHERE trip_joined_xref.outbound = True AND ts.tour_type != 'external'
