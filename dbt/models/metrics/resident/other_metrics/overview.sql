/*
-- Calculate overview table
Variable      Reference   Model
Households    ####        ####
Population    ####        ####
Stops         ####        ####
Tours         ####        ####
Trips         ####        ####
VMT           ####        ####
*/

with abm_households_cte as (
    select 
        count(distinct household_id) as abm_households,
    from {{ ref('stg_abm3_households') }}
),

abm_population_cte as (
    select
        count(distinct p.person_id) as abm_population,
    from {{ ref('stg_abm3_persons') }} as p
    join {{ ref('stg_abm3_households') }} as h 
    on p.household_id = h.household_id
),

abm_tours_cte as (
    select
        count(distinct t.tour_id) as abm_tours,
    from {{ ref('stg_abm3_tours') }} as t
    join {{ ref('stg_abm3_households') }} as h 
    on t.household_id = h.household_id
),

abm_trips_cte as (
    select
        sum(tr.weight_person_trip) as abm_trips,
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

abm_vmt_cte as (
    select
        sum(tr.distance_drive * tr.weight_trip) as abm_vmt
    from {{ ref('stg_abm3_trips') }} as tr
    join {{ ref('stg_abm3_households') }} as h 
    on tr.household_id = h.household_id
),

hts_totals_cte as (
    select 
        max(case when Variable = 'Households' then value else 0 end) as hts_households,
        max(case when Variable = 'Population' then value else 0 end) as hts_population,
        max(case when Variable = 'Tours' then value else 0 end) as hts_tours,
        max(case when Variable = 'Trips' then value else 0 end) as hts_trips,
        max(case when Variable = 'Stops' then value else 0 end) as hts_stops,
        max(case when Variable = 'VMT' then value else 0 end) as hts_vmt
    FROM {{ ref('stg_hts_totals') }}
),

hts_abm3_joined as (
    select 
        'Households' as Variables,
        hts_households as HTS,
        abm_households as ABM, 
    from hts_totals_cte, abm_households_cte
    
    union all 
    
    select 
        'Population' as Variables,
        hts_population as HTS,
        abm_population as ABM, 
    from hts_totals_cte, abm_population_cte
    
    union all 
    
    select 
        'Stops' as Variables,
        hts_stops as HTS,
        abm_stops as ABM,
    from hts_totals_cte, abm_stops_cte
        
    union all 

    select 
        'Tours' as Variables,
        hts_tours as HTS,
        abm_tours as ABM,
    from hts_totals_cte, abm_tours_cte

    union all 
    
    select 
        'Trips' as Variables,
        hts_trips as HTS,
        abm_trips as ABM,
    from hts_totals_cte, abm_trips_cte

    union all 
        
    select 
        'VMT' as Variables,
        hts_vmt as HTS,
        abm_vmt as ABM,
    from hts_totals_cte, abm_vmt_cte
)

select Variables, HTS, ABM
from hts_abm3_joined
