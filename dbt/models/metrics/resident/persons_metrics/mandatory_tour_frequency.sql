with abm3_source as (
    select person_type, hts_mtf as mtf_choice, COUNT(*) as freq
    from {{ ref('stg_abm3_persons') }} as person
    left join {{ ref('ptype_mapping') }} as ptype
    on person.ptype = ptype.ptype
    left join {{ ref('mtf_mapping') }} as mtf
    on person.mandatory_tour_frequency = mtf.abm_mtf
    where person.cdap_activity = 'M'
    group by hts_mtf, person_type   
),

hts_source as (
    select 
        PERTYPE as person_type, imf_choice as mtf_choice, freq
    FROM {{ ref('stg_hts_mandatoryFrequency') }}
),

hts_abm3_joined as (
    select 
        coalesce(a.person_type, h.person_type) as person_type, 
        coalesce(a.mtf_choice, h.mtf_choice) as mtf_choice, 
        coalesce(a.freq, 0) as abm_count, 
        coalesce(h.freq, 0) as hts_count
    from abm3_source a
    full join hts_source h
    on a.mtf_choice = h.mtf_choice and a.person_type = h.person_type
),

hts_abm3_total as (
    select 
        'Total' as person_type, 
        mtf_choice,
        sum(abm_count) as abm_count,
        sum(hts_count) as hts_count
    from hts_abm3_joined
    group by mtf_choice
)

select * from hts_abm3_joined
union all 
select * from hts_abm3_total