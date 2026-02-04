with trips_data as (
    select *
    from {{ ref('stg_obts_trip_targets') }}
)

select
    trips_data.trip_mode,
    trips_data.value,
    trips_data.tour_mode,
    coalesce(purpose_map.purpose_hts, trips_data.purpose)
        as purpose,
    trips_data.value
    / sum(trips_data.value)
        over (partition by trips_data.tour_mode, trips_data.purpose)
        as pct_of_total
from trips_data
left join {{ ref('purpose_mapping') }} as purpose_map
    on trips_data.purpose = purpose_map.purpose_abm3
