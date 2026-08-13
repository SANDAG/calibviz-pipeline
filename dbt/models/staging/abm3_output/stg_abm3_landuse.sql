with source as (
    {{ union_resident_land_use() }}
)

select
    scenario,
    mgra,
    exp_daily as daily_parking_expenditure
from source
