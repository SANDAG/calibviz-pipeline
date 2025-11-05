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

-- ABM totals
with abm_totals as (
    select         
        (select count(distinct household_id) from {{ ref('stg_abm3_households') }}) as abm_households,
        (select count(distinct person_id) from {{ ref('stg_abm3_persons') }}) as abm_population,
        (select count(distinct tour_id) from {{ ref('stg_abm3_tours') }}) as abm_tours,
        (select count(distinct trip_id) from {{ ref('stg_abm3_trips') }}) as abm_trips,
        (select sum(CAST(SUBSTRING(stop_frequency, 1, 1) AS INTEGER) + CAST(SUBSTRING(stop_frequency, 6, 1) AS INTEGER)) from {{ ref('stg_abm3_tours') }}) as abm_stops,
        (select sum(distance_drive * weight_trip) from {{ ref('stg_abm3_trips') }}) as abm_vmt
),

-- HTS totals
hts_totals as (
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
        abm_households as ABM
    from hts_totals, abm_totals
    
    union all 
    
    select 
        'Population' as Variables,
        hts_population as HTS,
        abm_population as ABM
    from hts_totals, abm_totals
    
    union all 
    
    select 
        'Tours' as Variables,
        hts_tours as HTS,
        abm_tours as ABM
    from hts_totals, abm_totals

    union all 
    
    select 
        'Trips' as Variables,
        hts_trips as HTS,
        abm_trips as ABM
    from hts_totals, abm_totals

    union all 
    
    select 
        'Stops' as Variables,
        hts_stops as HTS,
        abm_stops as ABM
    from hts_totals, abm_totals
        
    union all 
    
    select 
        'VMT' as Variables,
        hts_vmt as HTS,
        abm_vmt as ABM
    from hts_totals, abm_totals
)

select * from hts_abm3_joined
