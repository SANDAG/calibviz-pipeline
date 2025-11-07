with source as (SELECT * FROM {{ source('hts', 'totals') }})

SELECT 
  *
FROM source