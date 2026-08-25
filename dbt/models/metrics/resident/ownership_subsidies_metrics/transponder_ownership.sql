with abm3_source as (
    select
        scenario,
        case when transponder_ownership then 'Yes' else 'No' end as transponder_ownership,
        count(*) * 1.0 / sum(count(*)) over (partition by scenario) as proportion
    from {{ ref('stg_abm3_households') }} 
    group by scenario, case when transponder_ownership then 'Yes' else 'No' end
),

hts_source as (
    select 
        case when index then 'Yes' else 'No' end as transponder_ownership,  
        share as proportion 
    FROM {{ ref('stg_hts_transponderOwnership') }}
),

hts_abm3_joined as (
    select
        a.scenario,
        a.transponder_ownership, 
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.transponder_ownership = h.transponder_ownership
)

select * from hts_abm3_joined where transponder_ownership = 'Yes'
order by scenario