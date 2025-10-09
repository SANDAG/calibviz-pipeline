{{config(
    materialized='view',
    tags=['staging']
)}}


with source as (SELECT * FROM {{ source('abm3_resident_output', 'final_trips') }})

SELECT * FROM source