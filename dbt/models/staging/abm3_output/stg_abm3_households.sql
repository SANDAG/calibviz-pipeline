with source as (
  select *
  from {{ source('abm3_resident_output', 'final_households') }}
),
filter_columns as (
  select household_id,
    hhsize,
    auto_ownership,
    transponder_ownership,
    unittype,
    num_adults
  from source
),
filter_gq as (
  select * 
  from filter_columns
  where {{ include_gq_where('unittype') }}  -- -> will be "unittype = 0" if include_gq is false
)
select *
from filter_gq