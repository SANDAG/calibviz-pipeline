{{ config(
    materialized='view',
    tags=['staging']
)}}

with source as (
  SELECT * FROM {{ source ('abm3_resident_output', 'final_households') }}
),

hhsize_capped as (
  SELECT 
  *,
  --- add column capping hhsize at 5
  CASE 
    WHEN hhsize > 5 THEN 5 
    ELSE hhsize 
  END::INTEGER AS hhsize_capped
  FROM source
  --- remove group quarters
  WHERE unittype = 0
)

select * from hhsize_capped

