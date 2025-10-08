{{ config(
    materialized='table',
    tags=['staging']
)}}


SELECT * FROM {{ source('external_source', 'final_households')}}

---
WHERE unittype == 0