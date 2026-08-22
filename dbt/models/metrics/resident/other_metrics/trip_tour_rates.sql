-- Trip and tour rate summaries comparing ABM model outputs with HTS survey data
-- Includes per-household and per-person rates
-- Supports multiple ABM scenarios

with abm_metrics as (
    select 
        scenario,
        sum(trips) as trips,
        sum(households) as households,
        sum(population) as population,
        sum(total_participants) as total_participants,
        sum(total_stops) as total_stops,
        sum(vmt) as vmt
    from {{ ref('int_abm_hts_totals') }}
    where source = 'ABM'
    group by scenario
),

hts_metrics as (
    select 
        sum(trips) as trips,
        sum(households) as households,
        sum(population) as population,
        sum(total_participants) as total_participants,
        sum(total_stops) as total_stops,
        sum(vmt) as vmt
    from {{ ref('int_abm_hts_totals') }}
    where source = 'HTS'
)

select
    a.scenario,
    'Trips per Household' as metric,
    round(h.trips / nullif(h.households, 0), 2) as hts_value,
    round(a.trips / nullif(a.households, 0), 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    a.scenario,
    'Trips per Person' as metric,
    round(h.trips / nullif(h.population, 0), 2) as hts_value,
    round(a.trips / nullif(a.population, 0), 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

-- Tours per Person uses total_participants as proxy for total tours
select
    a.scenario,
    'Tours per Person' as metric,
    round(h.total_participants / nullif(h.population, 0), 2) as hts_value,
    round(a.total_participants / nullif(a.population, 0), 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    a.scenario,
    'Stops per Person' as metric,
    round(h.total_stops / nullif(h.population, 0), 2) as hts_value,
    round(a.total_stops / nullif(a.population, 0), 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a