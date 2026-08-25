with source as (
    {{ union_resident_tours() }}
),
filter_columns as (
    select
        scenario,
        tour_id,
        person_id,
        household_id,
        tour_type,
        tour_category, 
        number_of_participants,
        origin, 
        destination, 
        household_id, 
        tour_mode,
        stop_frequency,
        primary_purpose
    from source
),
filter_gq as (
    select *
    from filter_columns as tours
    left join {{ ref('stg_abm3_households') }} as households
    on tours.household_id = households.household_id
        and tours.scenario = households.scenario
    where {{ include_gq_where('unittype') }}  -- -> will be "unittype = 0" if include_gq is false
)
select *
from filter_gq