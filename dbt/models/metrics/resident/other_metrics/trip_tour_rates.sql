-- Trip and tour rate summaries comparing ABM model outputs with HTS survey data
-- Includes per-household and per-person rates
-- Supports multiple ABM scenarios

with abm_metrics as (
    select *
    from {{ ref('int_abm_hts_totals') }}
    where source = 'ABM'
),

hts_metrics as (
    select *
    from {{ ref('int_abm_hts_totals') }}
    where source = 'HTS'
)

select
    a.scenario,
    'Trips per Household' as metric,
    round(h.trips / h.households, 2) as hts_value,
    round(a.trips / a.households, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    a.scenario,
    'Trips per Person' as metric,
    round(h.trips / h.population, 2) as hts_value,
    round(a.trips / a.population, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

-- Tours per Person uses total_participants as proxy for total tours
select
    a.scenario,
    'Tours per Person' as metric,
    round(h.total_participants / h.population, 2) as hts_value,
    round(a.total_participants / a.population, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    a.scenario,
    'Stops per Person' as metric,
    round(h.total_stops / h.population, 2) as hts_value,
    round(a.total_stops / a.population, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a