{{ config(
    materialized='table',
    tags=['staging']
)}}




SELECT 
  *
FROM {{ source('hts', 'hhSizeDist') }}