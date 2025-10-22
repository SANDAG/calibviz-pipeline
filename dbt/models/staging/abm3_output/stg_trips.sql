with source as (
    select *
    from { { source ('abm3_resident_output', 'final_trips') } }
),
filter_columns as (
    select trip_id,
        tour_id,
        person_id,
        household_id,
        tour_participants,
        trip_mode,
        purpose,
        primary_purpose,
        trip_period,
        origin,
        destination,
        otaz,
        dtaz,
        parking_zone,
        trip_num,
        trip_count,
        owns_transponder,
        weight_trip,
        weight_person_trip
    from source
)
select *
from filter_columns