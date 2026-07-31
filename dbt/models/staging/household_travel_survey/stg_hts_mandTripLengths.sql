with source as (SELECT * FROM {{ source('hts', 'mandTripLengths') }})

SELECT 
  *
FROM source