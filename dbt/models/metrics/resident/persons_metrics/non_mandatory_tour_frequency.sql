with abm3_source as (
    select
        person.scenario,
        ptype.person_type,
        case
            when person.num_non_mand = 0 then '0'
            when person.num_non_mand = 1 then '1'
            when person.num_non_mand = 2 then '2'
            when person.num_non_mand >= 3 then '3+'
            else 'None'
        end as num_tours,
        COUNT(*) as freq
    from {{ ref('stg_abm3_persons') }} as person
    left join {{ ref('ptype_mapping') }} as ptype
        on person.ptype = ptype.ptype
    group by person.scenario, ptype.person_type, 
        case
            when person.num_non_mand = 0 then '0'
            when person.num_non_mand = 1 then '1'
            when person.num_non_mand = 2 then '2'
            when person.num_non_mand >= 3 then '3+'
            else 'None'
        end
),

hts_source as (
    select
        pertype as person_type,
        freq,
        CAST(nmtours as varchar) as num_tours
    from {{ ref('stg_hts_nonMandatoryFrequency') }}
),

hts_abm3_joined as (
    select
        a.scenario,
        COALESCE(a.person_type, h.person_type) as person_type,
        COALESCE(a.num_tours, h.num_tours) as num_tours,
        COALESCE(a.freq, 0) as abm_count,
        COALESCE(h.freq, 0) as hts_count
    from abm3_source as a
    full join hts_source as h
        on a.person_type = h.person_type and a.num_tours = h.num_tours
),

hts_abm3_total as (
    select
        scenario,
        'Total' as person_type,
        num_tours,
        SUM(abm_count) as abm_count,
        SUM(hts_count) as hts_count
    from hts_abm3_joined
    group by scenario, num_tours
)

select * from hts_abm3_joined
union all
select * from hts_abm3_total
order by scenario, person_type, num_tours
