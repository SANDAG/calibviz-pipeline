{{ config(
    materialized='table',
    tags=['staging']
)}}

with source as (
    select hhsize, count(*) * 100 / sum(count(*)) over () as percentage from {{ ref('stg_households') }} group by hhsize
)

select * from source
ORDER BY hhsize DESC
