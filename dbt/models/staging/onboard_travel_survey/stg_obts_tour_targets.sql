with base as (
    select *
    from {{ source('onboard_transit_survey', 'tour_mc_targets_final_disagg') }}
)

select
    *,
    case
        when grouped_tour_mode = 'TNC-REG' then 'TNC_SINGLE'
        else grouped_tour_mode
    end as tour_mode_remapped,
    case
        when purpose = 'Work sub-tour' then 'AtWork'
        else purpose
    end as tour_purpose_remapped,
    case
        when auto_suff = '0' then 'zeroautohh'
        when auto_suff = '1' then 'autodeficienthh'
        when auto_suff = '2' then 'autosufficienthh'
        else auto_suff
    end as auto_suff_mapped
from base
