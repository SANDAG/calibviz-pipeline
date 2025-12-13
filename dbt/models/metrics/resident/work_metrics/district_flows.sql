-- Calculate telecommute frequency
with abm3_source as (
    select home_pmsa.pmsa_name as home_district,
    work_pmsa.pmsa_name as work_district,
    count(*) as freq
    from {{ ref('stg_abm3_persons') }} as persons
    left join {{ ref('stg_abm3_households') }} as households
    on persons.household_id = households.household_id
    inner join {{ ref('mgra_taz_pmsa_xref') }} as home_mgra_pmsa_mapping
    on persons.home_zone_id = home_mgra_pmsa_mapping.MGRA
    inner join {{ ref('pmsa_name') }} as home_pmsa
    on home_mgra_pmsa_mapping.PSEUDOMSA = home_pmsa.pmsa_id
    inner join {{ ref('mgra_taz_pmsa_xref') }} as work_mgra_pmsa_mapping
    on persons.workplace_zone_id = work_mgra_pmsa_mapping.MGRA
    inner join {{ ref('pmsa_name') }} as work_pmsa
    on work_mgra_pmsa_mapping.PSEUDOMSA = work_pmsa.pmsa_id
    where persons.work_from_home = FALSE and 
    persons.workplace_zone_id > 0 and 
    persons.is_external_worker = FALSE and 
    {{ include_gq_where('households.unittype') }}  -- -> will be "households.unittype = 0" if include_gq is false
    group by home_pmsa.pmsa_name, work_pmsa.pmsa_name
    order by home_pmsa.pmsa_name, work_pmsa.pmsa_name
),

hts_source as (
    select
        HDISTRICT as home_district,
        WDISTRICT as work_district,
        round(freq, 0) as freq
    from {{ ref('stg_hts_districtFlows') }}
),

hts_abm3_joined as (
    select 
        a.home_district,
        a.work_district,
        a.freq as abm_total_workers,
        h.freq as hts_total_workers
    from abm3_source a
    full join hts_source h
    on a.home_district = h.home_district and a.work_district = h.work_district
),

hts_abm3_total as (
    select 
        'Total' as home_district, 
        work_district,
        sum(abm_total_workers) as abm_total_workers,
        sum(hts_total_workers) as hts_total_workers
    from hts_abm3_joined
    group by work_district
    order by work_district
)


select * from hts_abm3_joined
union all 
select * from hts_abm3_total