with source as (SELECT * FROM {{ source('hts', 'dapSummary_vis') }})

SELECT 
  *
FROM source