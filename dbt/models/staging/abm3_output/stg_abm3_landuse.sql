with source as (
    select *
    from {{ source('abm3_resident_output', 'final_land_use') }}
)

select
    mgra,
    exp_daily as daily_parking_expenditure
from source
