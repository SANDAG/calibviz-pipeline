-- models/staging/stg_final_households.sql
{{ config(
    materialized='external',
    location='local_duckdb_cache/final_households.parquet',
    format='parquet'
) }}

with source as (
  SELECT * FROM {{ source('abm3_resident_output', 'final_households') }}
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
  -- WHERE unittype = 0
)

SELECT * FROM hhsize_capped