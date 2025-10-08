with source as (
    select * from {{ source('staging', 'test_trips') }}
)

select
    *
from source