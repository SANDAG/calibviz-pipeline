with source as (SELECT * FROM {{ source('hts_2023', 'mandTLFD') }})

SELECT 
  *
FROM source
