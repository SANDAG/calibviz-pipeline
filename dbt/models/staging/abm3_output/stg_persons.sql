with source as (
    select *
    from {{ source('abm3_resident_output', 'final_persons') }}
),
filter_columns as (
    select person_id,
        ptype
    from source
)
select *
from filter_columns