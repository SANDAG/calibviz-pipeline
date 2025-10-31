with source as (SELECT * FROM {{ source('hts', 'tourModeProfile_vis') }})

SELECT 
  *
FROM source