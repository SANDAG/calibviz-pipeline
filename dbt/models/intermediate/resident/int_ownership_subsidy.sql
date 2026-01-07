-- models/intermediate/int_abm3_persons__with_person_type.sql
-- Reusable base that does the join once
select
    p.*,
    m.person_type,
    l.daily_parking_expenditure,
    p.free_parking_at_work::INTEGER * (1.0 / {{ var('sample_rate', 1.0) }})
    / SUM(
        case
            when l.daily_parking_expenditure > 0 then 1
            else 0
        end
    ) over (partition by m.person_type)
        as free_parking_weight
from {{ ref('stg_abm3_persons') }} as p
left join {{ ref('ptype_mapping') }} as m
    on p.ptype = m.ptype
left join {{ ref('stg_abm3_landuse') }} as l
    on p.workplace_zone_id = l.mgra
