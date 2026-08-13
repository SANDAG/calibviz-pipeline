with source as (SELECT * FROM {{ source('general_survey', 'departing_trips_by_mode') }}
)

SELECT
    * EXCLUDE (airport_access_mode, inbound_bool, person_trips, origin_pmsa),
    airport_access_mode as arrival_mode,
    inbound_bool as inbound,
    person_trips as weight_person_trip,
    origin_pmsa::INTEGER::VARCHAR -- convert to integer first to remove decimal point, then to string
FROM source