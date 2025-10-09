{{ config(
    materialized='table',
    tags=['staging']
)}}




SELECT 
  *,
  --- add column capping hhsize at 5
  CASE 
    WHEN hhsize > 5 THEN 5 
    ELSE hhsize 
  END::INTEGER AS hhsize_capped
FROM {{ source('external_source', 'final_households') }}
--- remove group quarters
WHERE unittype == 0