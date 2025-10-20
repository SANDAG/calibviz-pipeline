with source as (
    select 
        auto_ownership,
        count(*) * 100.0 / sum(count(*)) over () as percentage 
    from {{ ref('stg_households') }} 
    group by auto_ownership
),

hts_source as (
    select 
        HHVEH as auto_ownership, 
        FREQ * 100.0 / sum(FREQ) over () as percentage 
    FROM {{ ref('stg_autoOwnership') }}
),

hts_auto_joined as (
    select 
        s.auto_ownership, 
        s.percentage as abm_percentage, 
        h.percentage as hts_percentage
    from source s
    join hts_source h on s.auto_ownership = h.auto_ownership
)

select * from hts_auto_joined