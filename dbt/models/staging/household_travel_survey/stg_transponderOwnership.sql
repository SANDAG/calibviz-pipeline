with source as (select * from {{ source('hts', 'transponder_ownership') }})

select
    index as transponder,
    share
from source
