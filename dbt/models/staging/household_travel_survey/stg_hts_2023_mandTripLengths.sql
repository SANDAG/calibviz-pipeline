with source as (SELECT * FROM {{ source('hts_2023', 'mandTripLengths') }})

SELECT 
  *
FROM source
