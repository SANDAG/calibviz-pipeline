with tours_data as (
    select
        mode_map.mode_hts as tour_mode,
        tour_targets.freq_as0,
        tour_targets.freq_as1,
        tour_targets.freq_as2,
        tour_targets.freq_all,
        coalesce(purpose_map.purpose_hts, tour_targets.tour_purpose_mapped)
            as tour_purpose_mapped
    from {{ ref('stg_obts_tour_targets') }} as tour_targets
    left join
        {{ ref('purpose_mapping') }} as purpose_map
        on tour_targets.tour_purpose_mapped = purpose_map.purpose_abm3
    left join {{ ref('mode_mapping') }} as mode_map
        on tour_targets.tour_mode = mode_map.mode_abm3
),

tours_long_format as (
    select
        tour_mode,
        tour_purpose_mapped as tour_purpose,
        frequency as freq,
        replace(auto_sufficiency, 'freq_', '') as auto_sufficiency
    from tours_data
        unpivot
            (
                frequency for auto_sufficiency in (
                    freq_as0, freq_as1, freq_as2, freq_all
                )
        )
)

select
    tour_mode,
    tour_purpose as purpose,
    freq,
    case
        when auto_sufficiency = 'as0' then '0: No Vehicles'
        when auto_sufficiency = 'as1' then '1: 1+ Veh/Adults > Veh'
        when auto_sufficiency = 'as2' then '2: Vehicles >= Adults'
        else auto_sufficiency
    end as ownershipcategory,
    freq / max(case when tour_purpose = 'Total' then freq end)
        over (partition by tour_mode, auto_sufficiency) as pct_of_total
from tours_long_format
