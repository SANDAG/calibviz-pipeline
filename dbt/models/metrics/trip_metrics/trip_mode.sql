with source as (
    select 
        case 
            when trip_mode = 'DRIVEALONE' then '01: SOV'
            when trip_mode = 'SHARED2' then '02: Shared Ride 2'
            when trip_mode = 'SHARED3' then '03: Shared Ride 3+'
            else trip_mode
        end as trip_mode,
        sum(weight_person_trip) as count_trips,
        sum(weight_person_trip) * 1.0 / sum(sum(weight_person_trip)) over () as abm_share
    from {{ ref('stg_trips') }} 
    group by 
        case 
            when trip_mode = 'DRIVEALONE' then '01: SOV'
            when trip_mode = 'SHARED2' then '02: Shared Ride 2'
            when trip_mode = 'SHARED3' then '03: Shared Ride 3+'
            else trip_mode
        end
),

hts_source as (
     select 
        trip_mode,
        sum(value) as total_trips,
        sum(value) * 1.0 / sum(sum(value)) over () as hts_share
    from {{ ref('stg_tripMode') }}
    group by trip_mode
),


hts_trip_mode_joined as (
    select 
        s.trip_mode, 
        s.abm_share, 
        h.hts_share 
    from source s
    join hts_source h on s.trip_mode = h.trip_mode
)

select * from hts_trip_mode_joined

