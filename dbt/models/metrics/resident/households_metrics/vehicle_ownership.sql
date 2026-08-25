with abm3_source as (
    select 
        scenario,
        auto_ownership,
        count(*) * 1.0 / sum(count(*)) over (partition by scenario) as proportion
    from {{ ref('stg_abm3_households') }} 
    group by scenario, auto_ownership
),

hts_source as (
    select 
        HHVEH as auto_ownership,  
        FREQ * 1.0 / sum(FREQ) over () as proportion 
    FROM {{ ref('stg_hts_autoOwnership') }}
),

hts_abm3_joined as (
    select 
        a.scenario,
        a.auto_ownership, 
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.auto_ownership = h.auto_ownership
)

select * from hts_abm3_joined
order by scenario, auto_ownership