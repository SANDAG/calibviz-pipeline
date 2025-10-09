with

source as (
    select person_id, household_id, ptype from {{ source('abm3_resident_output', 'final_persons') }}
)

select * from source