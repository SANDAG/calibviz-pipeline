-- Calculate trip and tour rate summaries
-- Compares ABM3 model outputs with HTS survey data

with abm_base as (
    select
        (
            select count(distinct household_id)
            from {{ ref('stg_abm3_households') }}
        ) as households,
        (select count(distinct person_id) from {{ ref('stg_abm3_persons') }}
        ) as population,
        (select sum(number_of_participants) from {{ ref('stg_abm3_tours') }}
        ) as tours,
        (select sum(weight_person_trip) from {{ ref('stg_abm3_trips') }}
        ) as trips,
        (select sum(
            (
                cast(substring(stop_frequency, 1, 1) as integer)
                + cast(substring(stop_frequency, 6, 1) as integer)
            )
            * number_of_participants
        ) from {{ ref('stg_abm3_tours') }}) as stops
),

hts_base as (
    select
        max(case when variable = 'Households' then value end) as households,
        max(case when variable = 'Population' then value end) as population,
        max(case when variable = 'Tours' then value end) as tours,
        max(case when variable = 'Trips' then value end) as trips,
        max(case when variable = 'Stops' then value end) as stops
    from {{ ref('stg_hts_totals') }}
)

select
    'Trips per Household' as metric,
    round(h.trips / h.households, 2) as hts_value,
    round((a.trips / {{ var('sample_rate') }}) / a.households, 2) as abm_value
from hts_base as h
cross join abm_base as a

union all

select
    'Trips per Person' as metric,
    round(h.trips / h.population, 2) as hts_value,
    round((a.trips / {{ var('sample_rate') }}) / a.population, 2) as abm_value
from hts_base as h
cross join abm_base as a

union all

select
    'Tours per Person' as metric,
    round(h.tours / h.population, 2) as hts_value,
    round((a.tours / {{ var('sample_rate') }}) / a.population, 2) as abm_value
from hts_base as h
cross join abm_base as a

union all

select
    'Stops per Person' as metric,
    round(h.stops / h.population, 2) as hts_value,
    round((a.stops / {{ var('sample_rate') }}) / a.population, 2) as abm_value
from hts_base as h
cross join abm_base as a
