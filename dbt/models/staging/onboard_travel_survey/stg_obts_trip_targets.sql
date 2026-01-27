with base as (
    select *
    from {{ source('onboard_transit_survey', 'trip_mc_targets_final_disagg') }}
)

select * from base
