with source as (SELECT * FROM {{ source('hts', 'inmSummary_vis') }})

SELECT 
  *
FROM source