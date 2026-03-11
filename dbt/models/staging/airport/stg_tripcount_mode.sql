{{ config(
    materialized='table'
) }}

with trip_source as (
    {{ union_airport_trips() }}
),

tour_source as (
    {{ union_airport_tours() }}
),

mgra_taz_pmsa_xref as (
    SELECT 
    TAZ as taz,
    MGRA as mgra,
    PSEUDOMSA as origin_pmsa
    FROM {{ ref('mgra_taz_pmsa_xref') }}
),

origin_pmsa_xref as (
    SELECT *
    FROM (VALUES
        (1, 'DOWNTOWN'),
        (2, 'CENTRAL'),
        (3, 'NORTH_CITY'),
        (4, 'SOUTH_SUBURBAN'),
        (5, 'EAST_SUBURBAN'),
        (6, 'NORTH_COUNTY_WEST'),
        (7, 'NORTH_COUNTY_EAST'),
        (8, 'EAST_COUNTY'),
        (99, 'EXTERNAL')
    ) AS t(pmsa_id, pmsa_name)
),

trip_joined_xref as (
    SELECT
        ts.* EXCLUDE (origin_mgra),
        ts.origin_mgra,
        xref.origin_pmsa,
        pm.pmsa_name as origin_pmsa_name
    FROM trip_source ts
    LEFT JOIN mgra_taz_pmsa_xref xref 
        ON ts.origin_mgra = xref.mgra
    LEFT JOIN origin_pmsa_xref pm 
        ON xref.origin_pmsa = pm.pmsa_id
)

SELECT
    trip_joined_xref.scenario,
    origin_mgra,
    origin_pmsa_name::VARCHAR as origin_pmsa,
    CASE WHEN arrival_mode = 'TAXI_LOC1' THEN 'TAXI'
         WHEN arrival_mode = 'RIDEHAIL_LOC1' AND trip_mode = 'SHARED2' THEN 'TNC_SINGLE'
         WHEN arrival_mode = 'RIDEHAIL_LOC1' AND trip_mode = 'SHARED3' THEN 'TNC_SHARED'
         ELSE trip_mode
    END AS
    trip_mode,
    CASE WHEN ts.tour_type LIKE 'emp' THEN 'emp'
         WHEN ts.tour_type LIKE 'res_per%' THEN 'res_nb'
         WHEN ts.tour_type LIKE 'res_bus%' THEN 'res_bus'
         WHEN ts.tour_type LIKE 'vis_per%' THEN 'vis_nb'
         WHEN ts.tour_type LIKE 'vis_bus%' THEN 'vis_bus'
         ELSE ts.tour_type
    END AS tour_type,
    case 
        when ts.tour_type like 'res_%' then 'resident'
        when ts.tour_type like 'vis_%' then 'visitor'
        when ts.tour_type like 'emp%' then 'employee'
        else ts.tour_type
    end as tour_type_general,
    outbound,
    -- mode mapping
    -- amts.mapped_value as arrival_mode,
    COALESCE(m.final_mode, trip_joined_xref.arrival_mode) as arrival_mode,
    weight_person_trip as trip
FROM trip_joined_xref
JOIN tour_source ts 
    ON trip_joined_xref.tour_id = ts.tour_id 
    AND trip_joined_xref.scenario = ts.scenario
LEFT JOIN {{ ref('arrival_mode_mapping') }} m ON m.original_mode = trip_joined_xref.arrival_mode
-- JOIN {{ ref('arrival_mode_to_survey') }} amts USING (arrival_mode)
---JOIN {{ ref ('arrival_mode_mapping')}} m USING (arrival_mode)
WHERE trip_joined_xref.outbound = True AND ts.tour_type != 'external'
