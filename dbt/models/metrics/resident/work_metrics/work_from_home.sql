-- Calculate share of workers working from home by district (pmsa)
with abm3_source as (
    select
    pmsa.pmsa_name as district,
    count(*) as total_workers, 
    sum(case when persons.work_from_home = TRUE then 1 else 0 end) as wfh_workers,
    round(sum(case when persons.work_from_home = TRUE then 1 else 0 end) * 1.0 / count(*), 4) as wfh_share    
    from {{ ref('stg_abm3_persons') }} as persons
    left join {{ ref('stg_abm3_households') }} as households
    on persons.household_id = households.household_id
    left join {{ ref('mgra_taz_pmsa_xref') }} as mgra_pmsa_mapping
    on persons.home_zone_id = mgra_pmsa_mapping.MGRA
    inner join {{ ref('pmsa_name') }} as pmsa
    on mgra_pmsa_mapping.PSEUDOMSA = pmsa.pmsa_id
    where persons.is_worker = TRUE and
    {{ include_gq_where('households.unittype') }}  -- -> will be "households.unittype = 0" if include_gq is false
    group by pmsa.pmsa_name
    order by pmsa.pmsa_name
),

hts_source as (
    select 
        District as district,
        round(Workers, 0) as total_workers,
        round(WFH, 0) as wfh_workers,
        round("%WFH", 4) as wfh_share
    from {{ ref('stg_hts_wfhSummary') }}
    where district != 'Total'
),

hts_abm3_joined as (
    select 
        a.district, 
        a.total_workers as abm_total_workers, 
        h.total_workers as hts_total_workers,
        a.wfh_workers as abm_wfh_workers,
        h.wfh_workers as hts_wfh_workers,
        a.wfh_share as abm_proportion,
        h.wfh_share as hts_proportion
    from abm3_source a
    join hts_source h on a.district = h.district
)

select * from hts_abm3_joined
union all 
select 
    'Total' as district,
    sum(abm_total_workers) as abm_total_workers,
    sum(hts_total_workers) as hts_total_workers,
    sum(abm_wfh_workers) as abm_wfh_workers,
    sum(hts_wfh_workers) as hts_wfh_workers,
    round(sum(abm_wfh_workers) * 1.0 / sum(abm_total_workers), 4) as abm_proportion,
    round(sum(hts_wfh_workers) * 1.0 / sum(hts_total_workers), 4) as hts_proportion
from hts_abm3_joined