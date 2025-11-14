{{ config(
    materialized='table',
    enabled=false
) }}

SELECT *
FROM delta_scan( {{ source("databricks_calibration", "calib__tripcount_by_taz") }} )
