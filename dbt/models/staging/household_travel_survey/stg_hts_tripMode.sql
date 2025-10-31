with source as (SELECT * FROM {{ source('hts', 'tripModeProfile_vis') }})

SELECT 
  *
FROM source