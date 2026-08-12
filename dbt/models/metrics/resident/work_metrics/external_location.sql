-- Calculate share of workers working from home by district (pmsa)
with abm3_source as (
    select
    persons.scenario,
    'External Work Location' as metric,
    sum(case when persons.is_external_worker = TRUE then 1 else 0 end) * 1.0 / count(*) as external_share
    from {{ ref('stg_abm3_persons') }} as persons
    left join {{ ref('stg_abm3_households') }} as households
    on persons.household_id = households.household_id and persons.scenario = households.scenario
    where persons.is_worker = TRUE and
    {{ include_gq_where('households.unittype') }}  -- -> will be "households.unittype = 0" if include_gq is false
    group by persons.scenario
),

hts_source as (
    select 
        'External Work Location' as metric,
        workers as external_share
    from {{ ref('stg_hts_externalFrequency') }}
),

hts_abm3_joined as (
    select 
        a.scenario,
        a.metric, 
        a.external_share as abm_proportion,
        h.external_share as hts_proportion
    from abm3_source a
    join hts_source h
    on a.metric = h.metric
)

select * from hts_abm3_joined
order by scenario
