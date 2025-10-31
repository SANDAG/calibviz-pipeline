with source as (SELECT * FROM {{ source('hts', 'tmodeProfile_vis') }})

SELECT 
  *
FROM source