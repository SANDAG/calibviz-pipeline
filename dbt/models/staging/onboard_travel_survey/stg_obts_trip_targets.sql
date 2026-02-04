with base as (
    select *
    from {{ source('onboard_transit_survey', 'tripmodeProfile_vis_calib') }}
    where purpose != 'total'
),

fixed_tours as (
    select
        base.*,
        case
            when lower(base.tourmode) = 'schoolbus' then 'SCH_BUS'
            else upper(replace(base.tourmode, '-', '_'))
        end as tour_mode_mapped,
        case
            when base.purpose = 'sch' then 'school'
            else base.purpose
        end as tour_purpose_mapped,
        case
            when m.mode = 'DRIVE_ALONE' then 'DRIVEALONE'
            else m.mode
        end as tripmode_fixed
    from base
    left join {{ ref('obts_mode_mapping') }} as m
        on base.tripmode = m.mode_id
)

select
    fixed_tours.tour_purpose_mapped as purpose,
    fixed_tours.value,
    coalesce(mode_map.mode_hts, fixed_tours.tour_mode_mapped) as tour_mode,
    coalesce(mode_map_trip.mode_hts, fixed_tours.tripmode_fixed) as trip_mode
from fixed_tours
left join {{ ref('mode_mapping') }} as mode_map
    on fixed_tours.tour_mode_mapped = mode_map.mode_abm3
left join {{ ref('mode_mapping') }} as mode_map_trip
    on fixed_tours.tripmode_fixed = mode_map_trip.mode_abm3
