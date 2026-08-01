with source as (SELECT * FROM {{ source('hts', 'mandTLFD') }})

SELECT 
  *
FROM source