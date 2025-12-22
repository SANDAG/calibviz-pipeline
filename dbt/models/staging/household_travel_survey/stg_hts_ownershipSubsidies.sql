with source as (SELECT * FROM {{ source('hts', 'ownership_subsidies') }})

SELECT 
  *
FROM source