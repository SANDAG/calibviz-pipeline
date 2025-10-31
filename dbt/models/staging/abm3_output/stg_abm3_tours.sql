with source as (
    select *
    from {{ source('abm3_resident_output', 'final_tours') }}
),
filter_columns as (
    select
        tour_id,
        person_id,
        tour_type,
        tour_category, 
        number_of_participants,
        origin, 
        destination, 
        household_id, 
        tour_mode,
        primary_purpose
    from source
)
select *
from filter_columns