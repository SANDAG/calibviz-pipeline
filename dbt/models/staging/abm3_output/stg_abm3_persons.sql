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
        is_external_worker
    from source
)
select *
from filter_columns