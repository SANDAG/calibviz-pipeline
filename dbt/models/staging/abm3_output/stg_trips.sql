{{ config(
       materialized='external',
       location='local_duckdb_cache/final_trips.parquet',
       format='parquet'
   ) }}

{{ union_resident_trips() }}