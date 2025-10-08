{{config(
    materialized='view',
    tags=['staging']
)}}

SELECT * FROM {{ source('external_source', 'final_trips')}}