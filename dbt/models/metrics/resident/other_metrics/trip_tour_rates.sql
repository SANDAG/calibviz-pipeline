-- Trip and tour rate summaries comparing ABM model outputs with HTS survey data
-- Includes per-household and per-person rates

with abm_metrics as (
    select *
    from {{ ref('int_abm_hts_totals') }}
    where data_source = 'ABM'
),

hts_metrics as (
    select *
    from {{ ref('int_abm_hts_totals') }}
    where data_source = 'HTS'
)

select
    'Trips per Household' as metric,
    round(h.trips / h.households, 2) as hts_value,
    round((a.trips / {{ var('sample_rate') }}) / a.households, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    'Trips per Person' as metric,
    round(h.trips / h.population, 2) as hts_value,
    round((a.trips / {{ var('sample_rate') }}) / a.population, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    'Tours per Person' as metric,
    round(h.tours / h.population, 2) as hts_value,
    round((a.tours / {{ var('sample_rate') }}) / a.population, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a

union all

select
    'Stops per Person' as metric,
    round(h.stops / h.population, 2) as hts_value,
    round((a.stops / {{ var('sample_rate') }}) / a.population, 2) as abm_value
from hts_metrics as h
cross join abm_metrics as a