with base as (
    select *
    from {{ source('onboard_transit_survey', 'tripmodeProfile_vis_calib') }}
)

select
    base.*,
    m.mode as trip_mode,
    case
        when base.purpose = 'sch' then 'school'
        else base.purpose
    end as tour_purpose_mapped
from base
left join {{ ref('obts_mode_mapping') }} as m
    on base.tripmode = m.mode_id
