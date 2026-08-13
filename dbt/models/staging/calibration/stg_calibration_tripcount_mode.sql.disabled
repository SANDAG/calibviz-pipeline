{{ config(
    materialized='table',

) }}

SELECT *
FROM delta_scan( {{ source("databricks_calibration", "calib__tripcount_by_mode_choice") }} )
