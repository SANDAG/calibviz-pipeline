with source as (
    select *
    from {{ source('abm3_resident_output', 'final_persons') }}
),
filter_columns as (
    select person_id,
        ptype,
        household_id,
        home_zone_id,
        workplace_zone_id,
        is_worker,
        work_from_home,
        telecommute_frequency,
        is_out_of_home_worker,
        is_external_worker,
        transit_pass_subsidy,
        transit_pass_ownership,
        free_parking_at_work,
        cdap_activity,
        mandatory_tour_frequency,
        non_mandatory_tour_frequency
    from source
),
filter_gq as (
    select *
    from filter_columns as persons
    left join {{ ref('stg_abm3_households') }} as households
    on persons.household_id = households.household_id
    where {{ include_gq_where('unittype') }}  -- -> will be "unittype = 0" if include_gq is false
)
select *
from filter_gq