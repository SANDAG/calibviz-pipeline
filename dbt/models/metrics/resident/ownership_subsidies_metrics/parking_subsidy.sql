with abm3_source as (
    select person_type,
        SUM(CASE WHEN free_parking_at_work THEN 1 ELSE 0 END) / COUNT(*) as proportion
    from {{ ref('stg_abm3_persons') }} as p
    left join {{ ref('ptype_mapping') }} as m
    on p.ptype = m.ptype
    where p.ptype in (1, 2, 3, 6) 
    group by person_type
    order by person_type
),

hts_source as (
    select PERTYPE as person_type, free_parking_at_work as proportion
    FROM {{ ref('stg_hts_ownershipSubsidies') }}
),

hts_abm3_joined as (
    select 
        a.person_type, 
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.person_type = h.person_type
)

select * from hts_abm3_joined