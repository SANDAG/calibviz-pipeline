with base as (
    select *
    from {{ source('onboard_transit_survey', 'tourmodeProfile_vis_calib') }}
)

select
    base.*,
    m.mode as tour_mode,
    case
        when base.purpose = 'sch' then 'school'
        else base.purpose
    end as tour_purpose_mapped
from base
left join {{ ref('obts_mode_mapping') }} as m on base.id = m.mode_id
