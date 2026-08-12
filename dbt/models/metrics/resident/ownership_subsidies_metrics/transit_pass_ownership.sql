with abm3_source as (
    select
        p.scenario,
        person_type,
        SUM(CASE WHEN transit_pass_ownership = 1 THEN 1 ELSE 0 END) / COUNT(*) as proportion
    from {{ ref('stg_abm3_persons') }} as p
    left join {{ ref('ptype_mapping') }} as m
    on p.ptype = m.ptype
    group by p.scenario, person_type
),

hts_source as (
    select PERTYPE as person_type, transit_pass_ownership as proportion
    FROM {{ ref('stg_hts_ownershipSubsidies') }}
),

hts_abm3_joined as (
    select 
        a.scenario,
        a.person_type, 
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.person_type = h.person_type
)

select * from hts_abm3_joined
order by scenario, person_type