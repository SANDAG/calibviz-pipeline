-- Calculate household size distribution as a percentage of total households
-- Exclude group quarters (e.g., large institutions, dorms) from source staging (where unittype = 0)
-- Cap household sizes at 5+ for comparison with survey data

with source as (
    select 
        hhsize_capped as hhsize, 
        count(*) * 100.0 / sum(count(*)) over () as percentage 
    from {{ ref('stg_households') }} 
    group by hhsize_capped
),

hts_source as (
    select 
        hhsize, 
        FREQ * 100.0 / sum(FREQ) over () as percentage 
    FROM {{ ref('stg_hhsizeDist') }}
),

hts_households_joined as (
    select 
        s.hhsize, 
        s.percentage as stg_percentage, 
        h.percentage as hts_percentage
    from source s
    join hts_source h on s.hhsize = h.hhsize
)

select * from hts_households_joined