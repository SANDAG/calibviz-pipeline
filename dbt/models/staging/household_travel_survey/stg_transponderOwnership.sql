with source as (SELECT * FROM {{ source('hts', 'transponder_ownership') }})

SELECT 
  *
FROM source