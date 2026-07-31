{{ config(
       materialized='external',
       location='local_duckdb_cache/final_trips.parquet',
       format='parquet'
   ) }}

SELECT * FROM {{ source('abm3_resident_output', 'final_trips') }}