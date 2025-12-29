-- Calculate trip and tour rate summaries
-- Rates: trips per household, trips per person, tours per person, stops per person
-- Compares ABM3 model outputs with HTS survey data

with abm_households_cte as (
    select 
        count(distinct household_id) as abm_households
    from {{ ref('stg_abm3_households') }}
),

abm_population_cte as (
    select
        count(distinct p.person_id) as abm_population
    from {{ ref('stg_abm3_persons') }} as p
    join {{ ref('stg_abm3_households') }} as h 
    on p.household_id = h.household_id
),

abm_tours_cte as (
    select
        count(distinct t.tour_id) as abm_tours
    from {{ ref('stg_abm3_tours') }} as t
    join {{ ref('stg_abm3_households') }} as h 
    on t.household_id = h.household_id
),

abm_trips_cte as (
    select
        sum(tr.weight_person_trip) as abm_trips
    from {{ ref('stg_abm3_trips') }} as tr
    join {{ ref('stg_abm3_households') }} as h 
    on tr.household_id = h.household_id
),

abm_stops_cte as (
    select
        sum(
            cast(substring(t.stop_frequency, 1, 1) as integer) + 
            cast(substring(t.stop_frequency, 6, 1) as integer)
        ) as abm_stops
    from {{ ref('stg_abm3_tours') }} as t
    join {{ ref('stg_abm3_households') }} as h 
    on t.household_id = h.household_id
),

hts_totals_cte as (
    select 
        max(case when Variable = 'Households' then value else 0 end) as hts_households,
        max(case when Variable = 'Population' then value else 0 end) as hts_population,
        max(case when Variable = 'Tours' then value else 0 end) as hts_tours,
        max(case when Variable = 'Trips' then value else 0 end) as hts_trips,
        max(case when Variable = 'Stops' then value else 0 end) as hts_stops
    from {{ ref('stg_hts_totals') }}
),

rate_calculations as (
    -- Trips per Household
    select 
        'Trips per Household' as metric,
        round(hts_trips / hts_households, 2) as hts_value,
        round((abm_trips / {{ var('sample_rate') }}) / abm_households, 2) as abm_value
    from hts_totals_cte, abm_households_cte, abm_trips_cte
    
    union all
    
    -- Trips per Person
    select 
        'Trips per Person' as metric,
        round(hts_trips / hts_population, 2) as hts_value,
        round((abm_trips / {{ var('sample_rate') }}) / abm_population, 2) as abm_value
    from hts_totals_cte, abm_population_cte, abm_trips_cte
    
    union all
    
    -- Tours per Person
    select 
        'Tours per Person' as metric,
        round(hts_tours / hts_population, 2) as hts_value,
        round((abm_tours / {{ var('sample_rate') }}) / abm_population, 2) as abm_value
    from hts_totals_cte, abm_population_cte, abm_tours_cte
    
    union all
    
    -- Stops per Person
    select 
        'Stops per Person' as metric,
        round(hts_stops / hts_population, 2) as hts_value,
        round((abm_stops / {{ var('sample_rate') }}) / abm_population, 2) as abm_value
    from hts_totals_cte, abm_population_cte, abm_stops_cte
)

select * from rate_calculations
