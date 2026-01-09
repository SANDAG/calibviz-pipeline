with source as (
    select *
    from read_csv({{ source('abm3_resident_output', 'final_trips') }}, ignore_errors=true)
),
filter_columns as (
    select trip_id,
        tour_id,
        household_id,
        trip_mode,
        purpose, -- destination purpose
        primary_purpose,
        trip_period,
        origin,
        destination,
        otaz,
        dtaz,
        distance_drive,
        weight_trip,
        weight_person_trip,
        inbound
    from source
),
filter_gq as (
    select *
    from filter_columns as trips
    left join {{ ref('stg_abm3_households') }} as households
    on trips.household_id = households.household_id
    where {{ include_gq_where('unittype') }}  -- -> will be "unittype = 0" if include_gq is false
)
select *
from filter_gq