with source as (
    select *
    from {{ source('abm3_resident_output', 'final_trips') }}
),
filter_columns as (
    select trip_id,
        tour_id,
        household_id,
        trip_mode,
        purpose,
        primary_purpose,
        trip_period,
        origin,
        destination,
        otaz,
        dtaz,
        distance_drive,
        weight_trip,
        weight_person_trip
    from source
)
select *
from filter_columns