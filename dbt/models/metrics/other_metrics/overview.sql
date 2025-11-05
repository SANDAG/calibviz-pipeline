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

with abm_totals as (
    select         
        -- Total households
        (select count(distinct household_id) from {{ ref('stg_abm3_households') }}) as abm_households,
        (select count(distinct household_id) from {{ ref('stg_abm3_households') }} where unittype = 0) as abm_households_nongq,
        (select count(distinct household_id) from {{ ref('stg_abm3_households') }} where unittype = 1) as abm_households_gq,
        
        -- Total population
        (select count(distinct person_id) from {{ ref('stg_abm3_persons') }}) as abm_population,
        (select count(distinct p.person_id) 
         from {{ ref('stg_abm3_persons') }} as p
         join {{ ref('stg_abm3_households') }} as h on p.household_id = h.household_id
         where h.unittype = 0) as abm_population_nongq,
        (select count(distinct p.person_id) 
         from {{ ref('stg_abm3_persons') }} as p
         join {{ ref('stg_abm3_households') }} as h on p.household_id = h.household_id
         where h.unittype = 1) as abm_population_gq,
        
        -- Total tours
        (select count(distinct tour_id) from {{ ref('stg_abm3_tours') }}) as abm_tours,
        (select count(distinct t.tour_id) 
         from {{ ref('stg_abm3_tours') }} as t
         join {{ ref('stg_abm3_households') }} as h on t.household_id = h.household_id
         where h.unittype = 0) as abm_tours_nongq,
        (select count(distinct t.tour_id) 
         from {{ ref('stg_abm3_tours') }} as t
         join {{ ref('stg_abm3_households') }} as h on t.household_id = h.household_id
         where h.unittype = 1) as abm_tours_gq,
        
        -- Total trips
        (select sum(weight_person_trip) from {{ ref('stg_abm3_trips') }}) as abm_trips,
        (select sum(tr.weight_person_trip) 
         from {{ ref('stg_abm3_trips') }} as tr
         join {{ ref('stg_abm3_households') }} as h on tr.household_id = h.household_id
         where h.unittype = 0) as abm_trips_nongq,
        (select sum(tr.weight_person_trip) 
         from {{ ref('stg_abm3_trips') }} as tr
         join {{ ref('stg_abm3_households') }} as h on tr.household_id = h.household_id
         where h.unittype = 1) as abm_trips_gq,
        
        -- Total stops
        (select sum(CAST(SUBSTRING(stop_frequency, 1, 1) AS INTEGER) + CAST(SUBSTRING(stop_frequency, 6, 1) AS INTEGER)) 
         from {{ ref('stg_abm3_tours') }}) as abm_stops,
        (select sum(CAST(SUBSTRING(t.stop_frequency, 1, 1) AS INTEGER) + CAST(SUBSTRING(t.stop_frequency, 6, 1) AS INTEGER))
         from {{ ref('stg_abm3_tours') }} as t
         join {{ ref('stg_abm3_households') }} as h on t.household_id = h.household_id
         where h.unittype = 0) as abm_stops_nongq,
        (select sum(CAST(SUBSTRING(t.stop_frequency, 1, 1) AS INTEGER) + CAST(SUBSTRING(t.stop_frequency, 6, 1) AS INTEGER))
         from {{ ref('stg_abm3_tours') }} as t
         join {{ ref('stg_abm3_households') }} as h on t.household_id = h.household_id
         where h.unittype = 1) as abm_stops_gq,
        
        -- Total VMT
        (select sum(distance_drive * weight_trip) from {{ ref('stg_abm3_trips') }}) as abm_vmt,
        (select sum(tr.distance_drive * tr.weight_trip) 
         from {{ ref('stg_abm3_trips') }} as tr
         join {{ ref('stg_abm3_households') }} as h on tr.household_id = h.household_id
         where h.unittype = 0) as abm_vmt_nongq,
        (select sum(tr.distance_drive * tr.weight_trip) 
         from {{ ref('stg_abm3_trips') }} as tr
         join {{ ref('stg_abm3_households') }} as h on tr.household_id = h.household_id
         where h.unittype = 1) as abm_vmt_gq
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
        abm_households as ABM, 
        abm_households_nongq as ABM_NonGQ,
        abm_households_gq as ABM_GQ
    from hts_totals, abm_totals
    
    union all 
    
    select 
        'Population' as Variables,
        hts_population as HTS,
        abm_population as ABM, 
        abm_population_nongq as ABM_NonGQ,
        abm_population_gq as ABM_GQ
    from hts_totals, abm_totals
    
    union all 
    
    select 
        'Tours' as Variables,
        hts_tours as HTS,
        abm_tours as ABM,
        abm_tours_nongq as ABM_NonGQ,
        abm_tours_gq as ABM_GQ
    from hts_totals, abm_totals

    union all 
    
    select 
        'Trips' as Variables,
        hts_trips as HTS,
        abm_trips as ABM,
        abm_trips_nongq as ABM_NonGQ,
        abm_trips_gq as ABM_GQ
    from hts_totals, abm_totals

    union all 
    
    select 
        'Stops' as Variables,
        hts_stops as HTS,
        abm_stops as ABM,
        abm_stops_nongq as ABM_NonGQ,
        abm_stops_gq as ABM_GQ
    from hts_totals, abm_totals
        
    union all 
    
    select 
        'VMT' as Variables,
        hts_vmt as HTS,
        abm_vmt as ABM,
        abm_vmt_nongq as ABM_NonGQ,
        abm_vmt_gq as ABM_GQ
    from hts_totals, abm_totals
)

select Variables, HTS, ABM, 
    case when ABM_NonGQ is not null then ABM_NonGQ else 0 end as ABM_NonGQ,
    case when ABM_GQ is not null then ABM_GQ else 0 end as ABM_GQ
from hts_abm3_joined
