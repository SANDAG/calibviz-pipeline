with source as (SELECT * FROM {{ source('hts', 'mtfSummary_vis') }})

SELECT 
  *
FROM source