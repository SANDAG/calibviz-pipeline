with abm3_source as (
    select
        coalesce(m.trip_mode_hts, t.trip_mode) as trip_mode,
        sum(t.weight_person_trip) as count_trips,
        sum(t.weight_person_trip) * 1.0 
            / sum(sum(t.weight_person_trip)) over () as abm_share
    from {{ ref('stg_trips') }} as t
    left join {{ ref('trip_mode_mapping') }} as m
        on t.trip_mode = m.trip_mode_abm3
    group by coalesce(m.trip_mode_hts, t.trip_mode)
),

hts_source as (
     select 
        trip_mode,
        sum(value) as total_trips,
        sum(value) * 1.0 / sum(sum(value)) over () as hts_share
    from {{ ref('stg_tripMode') }}
    group by trip_mode
),


hts_abm3_trip_mode_joined as (
    select 
        s.trip_mode, 
        s.abm_share, 
        h.hts_share 
    from abm3_source s
    join hts_source h on s.trip_mode = h.trip_mode
)

select * from hts_abm3_trip_mode_joined

