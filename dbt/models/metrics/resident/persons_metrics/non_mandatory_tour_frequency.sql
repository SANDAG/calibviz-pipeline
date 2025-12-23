with abm3_source as (
    select person_type, 
        case
            when non_mandatory_tour_frequency = 0 then '0'
            when non_mandatory_tour_frequency = 1 then '1'
            when non_mandatory_tour_frequency = 2 then '2'
            when non_mandatory_tour_frequency >= 3 then '3+'
            else 'None'
        end as num_tours, COUNT(*) as freq
    from {{ ref('stg_abm3_persons') }} as person
    left join {{ ref('ptype_mapping') }} as ptype
    on person.ptype = ptype.ptype
    group by 1, 2
),

hts_source as (
    select 
        PERTYPE as person_type, cast(nmtours as varchar) as num_tours, freq
    FROM {{ ref('stg_hts_nonMandatoryFrequency') }}
),

hts_abm3_joined as (
    select 
        coalesce(a.person_type, h.person_type) as person_type, 
        coalesce(a.num_tours, h.num_tours) as num_tours, 
        coalesce(a.freq, 0) as abm_count, 
        coalesce(h.freq, 0) as hts_count
    from abm3_source a
    full join hts_source h
    on a.person_type = h.person_type and a.num_tours = h.num_tours
),

hts_abm3_total as (
    select 
        'Total' as person_type, 
        num_tours,
        sum(abm_count) as abm_count,
        sum(hts_count) as hts_count
    from hts_abm3_joined
    group by num_tours
)

select * from hts_abm3_joined
union all 
select * from hts_abm3_total