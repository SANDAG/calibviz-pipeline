with abm3_source as (
    select scenario, person_type, hts_cdap as activity_pattern, COUNT(*) as freq
    from {{ ref('stg_abm3_persons') }} as person
    left join {{ ref('ptype_mapping') }} as ptype
    on person.ptype = ptype.ptype
    left join {{ ref('cdap_mapping') }} as cdap
    on person.cdap_activity = cdap.abm_cdap
    group by scenario, hts_cdap, person_type
),

hts_source as (
    select 
        PERTYPE as person_type, activity_pattern, freq
    FROM {{ ref('stg_hts_activityPattern') }}
),

hts_abm3_joined as (
    select 
        a.scenario,
        a.person_type, 
        a.activity_pattern, 
        a.freq as abm_count, 
        h.freq as hts_count
    from abm3_source a
    join hts_source h
    on a.person_type = h.person_type and a.activity_pattern = h.activity_pattern
),

hts_abm3_total as (
    select 
        scenario,
        'Total' as person_type, 
        activity_pattern,
        sum(abm_count) as abm_count,
        sum(hts_count) as hts_count
    from hts_abm3_joined
    group by scenario, activity_pattern
)

select * from hts_abm3_joined
union all 
select * from hts_abm3_total
order by scenario, person_type, activity_pattern