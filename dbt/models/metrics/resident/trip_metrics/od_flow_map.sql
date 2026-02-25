{{
    config(
        materialized='table',
        schema='metrics'
    )
}}

-- Aggregate trip flows by origin-destination pairs
-- Includes mode, time period, and geographic data for mapping
with trip_flows as (
    select
        t.otaz as origin_taz,
        t.dtaz as destination_taz,
        t.trip_mode,
        t.trip_period,
        count(*) as trip_count,
        sum(t.distance_total) as total_distance_miles,
        avg(t.distance_total) as avg_distance_miles,
        avg(t.time_total) as avg_time_minutes,
        sum(t.weight_trip) as weighted_trips
    from {{ ref('stg_abm3_trips') }} as t
    where 
        t.otaz is not null 
        and t.dtaz is not null
        and t.otaz != t.dtaz  -- Exclude intra-zonal trips for OD visualization
    group by 
        t.otaz,
        t.dtaz,
        t.trip_mode,
        t.trip_period
),

-- Add origin TAZ geography
flows_with_origin as (
    select
        tf.*,
        o_taz.longitude as origin_lon,
        o_taz.latitude as origin_lat,
        o_taz.name as origin_name
    from trip_flows as tf
    left join {{ ref('taz_centroids') }} as o_taz
        on tf.origin_taz = o_taz.taz
),

-- Add destination TAZ geography
flows_with_dest as (
    select
        fwo.*,
        d_taz.longitude as dest_lon,
        d_taz.latitude as dest_lat,
        d_taz.name as dest_name
    from flows_with_origin as fwo
    left join {{ ref('taz_centroids') }} as d_taz
        on fwo.destination_taz = d_taz.taz
),

-- Add mode mapping for readable names
final_flows as (
    select
        fwd.*,
        coalesce(m.mode_hts, fwd.trip_mode) as mode_name
    from flows_with_dest as fwd
    left join {{ ref('mode_mapping') }} as m
        on fwd.trip_mode = m.mode_abm3
)

select
    origin_taz,
    destination_taz,
    trip_mode,
    mode_name,
    trip_period,
    trip_count,
    weighted_trips,
    total_distance_miles,
    avg_distance_miles,
    avg_time_minutes,
    origin_lon,
    origin_lat,
    origin_name,
    dest_lon,
    dest_lat,
    dest_name
from final_flows
where 
    origin_lon is not null 
    and origin_lat is not null
    and dest_lon is not null 
    and dest_lat is not null
order by weighted_trips desc
