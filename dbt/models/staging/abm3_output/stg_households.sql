with source as (
  select *
  from {{ source('abm3_resident_output', 'final_households') }}
),
filter_columns as (
  select household_id,
    hhsize,
    auto_ownership,
    unittype
  from source
)
select *
from filter_columns