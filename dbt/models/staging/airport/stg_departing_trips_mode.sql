with source as (SELECT *,
    case 
        when tour_type like 'res_%' then 'resident'
        when tour_type like 'vis_%' then 'visitor'
        when tour_type like 'emp%' then 'employee'
        else tour_type
    end as tour_type_general
 FROM {{ source('general_survey', 'departing_trips_by_mode') }}
),

arrival_mode_mapping as (
    SELECT 
        arrival_mode,
        mapped_mode
    FROM {{ ref ('arrival_mode_mapping') }}
)

SELECT
    * EXCLUDE (airport_access_mode, inbound_bool, person_trips, origin_pmsa),
    COALESCE(m.mapped_mode, s.airport_access_mode ) as arrival_mode,
    -- airport_access_mode as arrival_mode,
    inbound_bool as inbound,
    person_trips as trip,
    origin_pmsa::INTEGER::VARCHAR as origin_pmsa-- convert to integer first to remove decimal point, then to string,
FROM source s
JOIN arrival_mode_mapping m ON s.airport_access_mode = m.arrival_mode