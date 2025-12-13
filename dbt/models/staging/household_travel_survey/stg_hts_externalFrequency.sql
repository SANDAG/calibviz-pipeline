with source as (SELECT * FROM {{ source('hts', 'externalFrequency') }})

SELECT 
  *
FROM source