with source as (SELECT * FROM {{ source('hts', 'hhSizeDist') }})

SELECT 
  *
FROM source