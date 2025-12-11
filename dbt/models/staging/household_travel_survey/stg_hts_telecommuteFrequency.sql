with source as (SELECT * FROM {{ source('hts', 'telecommute_frequency') }})

SELECT 
  *
FROM source