with source as (SELECT * FROM {{ source('hts', 'wfh_summary') }})

SELECT 
  *
FROM source