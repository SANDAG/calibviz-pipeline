with source as (SELECT * FROM {{ source('hts', 'autoOwnership') }})

SELECT 
  *
FROM source