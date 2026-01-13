-- Trip and tour rate summaries comparing ABM model outputs with HTS survey data
-- Includes per-household and per-person rates

with households as (
    select
        hts as hts_households,
        abm as abm_households
    from {{ ref('int_abm_hts_totals_long') }}
    where variables = 'Households'
),

population as (
    select
        hts as hts_population,
        abm as abm_population
    from {{ ref('int_abm_hts_totals_long') }}
    where variables = 'Population'
),

trips as (
    select
        hts as hts_trips,
        abm as abm_trips
   from {{ ref('int_abm_hts_totals_long') }}
    where variables = 'Trips'
),

tours as (
    select
        hts as hts_tours,
        abm as abm_tours
    from {{ ref('int_abm_hts_totals_long') }}
    where variables = 'Tours'
),

stops as (
    select
        hts as hts_stops,
        abm as abm_stops
   from {{ ref('int_abm_hts_totals_long') }}
    where variables = 'Stops'
)

select
    'Trips per Household' as variables,
    trips.hts_trips / households.hts_households as hts,
    trips.abm_trips / households.abm_households as abm
from trips
cross join households

union all

select
    'Trips per Person',
    trips.hts_trips / population.hts_population,
    trips.abm_trips / population.abm_population
from trips
cross join population

union all

select
    'Tours per Person',
    tours.hts_tours / population.hts_population,
    tours.abm_tours / population.abm_population
from tours
cross join population

union all

select
    'Stops per Person',
    stops.hts_stops / population.hts_population,
    stops.abm_stops / population.abm_population
from stops
cross join population
