{{ config(
    materialized='table'
) }}

with trip_source as (
    {{ union_airport_trips() }}
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
        ts.*,
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
    trip_joined_xref.primary_purpose,
    trip_joined_xref.outbound,
    CASE WHEN arrival_mode = 'TAXI_LOC1' THEN 'TAXI'
         WHEN arrival_mode = 'RIDEHAIL_LOC1' AND trip_mode = 'SHARED2' THEN 'TNC_SINGLE'
         WHEN arrival_mode = 'RIDEHAIL_LOC1' AND trip_mode = 'SHARED3' THEN 'TNC_SHARED'
         ELSE trip_mode
    END AS
    trip_mode,
    CASE WHEN trip_joined_xref.primary_purpose LIKE 'external%' THEN 'external'
         WHEN trip_joined_xref.primary_purpose LIKE 'res_per%' THEN 'res_nb'
         WHEN trip_joined_xref.primary_purpose LIKE 'res_bus%' THEN 'res_bus'
         WHEN trip_joined_xref.primary_purpose LIKE 'vis_per%' THEN 'vis_nb'
         WHEN trip_joined_xref.primary_purpose LIKE 'vis_bus%' THEN 'vis_bus'
         ELSE trip_joined_xref.primary_purpose
    END AS tour_type,
    case 
        when trip_joined_xref.primary_purpose like 'res_%' then 'resident'
        when trip_joined_xref.primary_purpose like 'vis_%' then 'visitor'
        when trip_joined_xref.primary_purpose like 'external%' then 'external'
        else trip_joined_xref.primary_purpose
    end as tour_type_general,
    -- mode mapping
    COALESCE(m.final_mode, trip_joined_xref.arrival_mode) as arrival_mode,
    weight_trip as trip,
    weight_person_trip as person_trip
FROM trip_joined_xref
LEFT JOIN {{ ref('arrival_mode_mapping') }} m ON m.original_mode = trip_joined_xref.arrival_mode
WHERE primary_purpose NOT LIKE '%_return%'