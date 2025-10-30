with abm3_source as (
    select 
        case when transponder_ownership then 'Yes' else 'No' end as transponder_ownership,
        'non-GQ' as household_type,
        count(*) * 1.0 / sum(count(*)) over () as proportion
    from {{ ref('stg_households') }} 
    where unittype = 0 --non-GQ only
    group by transponder_ownership, household_type
    UNION ALL
    select 
        case when transponder_ownership then 'Yes' else 'No' end as transponder_ownership,
        'all households (includes GQ)' as household_type,
        count(*) * 1.0 / sum(count(*)) over () as proportion
    from {{ ref('stg_households') }} 
    --where unittype = 0 --all households including GQ
    group by transponder_ownership,household_type
),

hts_source as (
    select 
        case when transponder then 'Yes' else 'No' end as transponder_ownership,  
        share as proportion 
    FROM {{ ref('stg_transponderOwnership') }}
),

hts_abm3_joined as (
    select 
        a.transponder_ownership, 
        a.household_type,
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.transponder_ownership = h.transponder_ownership
)

select * from hts_abm3_joined where transponder_ownership = 'Yes'