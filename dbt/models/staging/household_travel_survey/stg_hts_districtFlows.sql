with source as (SELECT * FROM {{ source('hts', 'districtFlows') }})

SELECT 
  *
FROM source