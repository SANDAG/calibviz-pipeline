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
        count(distinct case when unittype = 0 then household_id end) as abm_households_nongq,
        count(distinct case when unittype = 1 then household_id end) as abm_households_gq
    from {{ ref('stg_abm3_households') }}
),

abm_population_cte as (
    select
        count(distinct p.person_id) as abm_population,
        count(distinct case when h.unittype = 0 then p.person_id end) as abm_population_nongq,
        count(distinct case when h.unittype = 1 then p.person_id end) as abm_population_gq
    from {{ ref('stg_abm3_persons') }} as p
    join {{ ref('stg_abm3_households') }} as h 
    on p.household_id = h.household_id
),

abm_tours_cte as (
    select
        count(distinct t.tour_id) as abm_tours,
        count(distinct case when h.unittype = 0 then t.tour_id end) as abm_tours_nongq,
        count(distinct case when h.unittype = 1 then t.tour_id end) as abm_tours_gq
    from {{ ref('stg_abm3_tours') }} as t
    join {{ ref('stg_abm3_households') }} as h 
    on t.household_id = h.household_id
),

abm_trips_cte as (
    select
        sum(tr.weight_person_trip) as abm_trips,
        sum(case when h.unittype = 0 then tr.weight_person_trip end) as abm_trips_nongq,
        sum(case when h.unittype = 1 then tr.weight_person_trip end) as abm_trips_gq
    from {{ ref('stg_abm3_trips') }} as tr
    join {{ ref('stg_abm3_households') }} as h 
    on tr.household_id = h.household_id
),

abm_stops_cte as (
    select
        sum(
            cast(substring(t.stop_frequency, 1, 1) as integer) + 
            cast(substring(t.stop_frequency, 6, 1) as integer)
        ) as abm_stops,
        sum(
            case when h.unittype = 0 then 
                cast(substring(t.stop_frequency, 1, 1) as integer) + 
                cast(substring(t.stop_frequency, 6, 1) as integer)
            end
        ) as abm_stops_nongq,
        sum(
            case when h.unittype = 1 then 
                cast(substring(t.stop_frequency, 1, 1) as integer) + 
                cast(substring(t.stop_frequency, 6, 1) as integer)
            end
        ) as abm_stops_gq
    from {{ ref('stg_abm3_tours') }} as t
    join {{ ref('stg_abm3_households') }} as h 
    on t.household_id = h.household_id
),

abm_vmt_cte as (
    select
        sum(tr.distance_drive * tr.weight_trip) as abm_vmt,
        sum(case when h.unittype = 0 then tr.distance_drive * tr.weight_trip end) as abm_vmt_nongq,
        sum(case when h.unittype = 1 then tr.distance_drive * tr.weight_trip end) as abm_vmt_gq
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
        abm_households_nongq as ABM_NonGQ,
        abm_households_gq as ABM_GQ
    from hts_totals_cte, abm_households_cte
    
    union all 
    
    select 
        'Population' as Variables,
        hts_population as HTS,
        abm_population as ABM, 
        abm_population_nongq as ABM_NonGQ,
        abm_population_gq as ABM_GQ
    from hts_totals_cte, abm_population_cte
    
    union all 
    
    select 
        'Tours' as Variables,
        hts_tours as HTS,
        abm_tours as ABM,
        abm_tours_nongq as ABM_NonGQ,
        abm_tours_gq as ABM_GQ
    from hts_totals_cte, abm_tours_cte

    union all 
    
    select 
        'Trips' as Variables,
        hts_trips as HTS,
        abm_trips as ABM,
        abm_trips_nongq as ABM_NonGQ,
        abm_trips_gq as ABM_GQ
    from hts_totals_cte, abm_trips_cte

    union all 
    
    select 
        'Stops' as Variables,
        hts_stops as HTS,
        abm_stops as ABM,
        abm_stops_nongq as ABM_NonGQ,
        abm_stops_gq as ABM_GQ
    from hts_totals_cte, abm_stops_cte
        
    union all 
    
    select 
        'VMT' as Variables,
        hts_vmt as HTS,
        abm_vmt as ABM,
        abm_vmt_nongq as ABM_NonGQ,
        abm_vmt_gq as ABM_GQ
    from hts_totals_cte, abm_vmt_cte
)

select Variables, HTS, ABM, 
    COALESCE(ABM_NonGQ, 0) as ABM_NonGQ,
    COALESCE(ABM_GQ, 0) as ABM_GQ
from hts_abm3_joined
