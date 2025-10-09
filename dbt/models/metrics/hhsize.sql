{{ config(
    materialized='table',
    tags=['staging']
)}}

-- Calculate household size distribution as a percentage of total households
-- Exclude group quarters (e.g., large institutions, dorms) from source staging (where unittype = 0)
-- Cap household sizes at 5+ for comparison with survey data


with source as (
    select hhsize_capped, count(*) * 100 / sum(count(*)) over () as percentage from {{ ref('stg_households') }} group by hhsize_capped
)

select * from source
ORDER BY hhsize_capped DESC
