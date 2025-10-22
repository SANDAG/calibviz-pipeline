with abm3_source as (
    select 
        auto_ownership,
        count(*) * 1.0 / sum(count(*)) over () as proportion
    from {{ ref('stg_households') }} 
    group by auto_ownership
),

hts_source as (
    select 
        HHVEH as auto_ownership,  
        FREQ * 1.0 / sum(FREQ) over () as proportion 
    FROM {{ ref('stg_autoOwnership') }}
),

hts_abm3_joined as (
    select 
        a.auto_ownership, 
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.auto_ownership = h.auto_ownership
)

select * from hts_abm3_joined