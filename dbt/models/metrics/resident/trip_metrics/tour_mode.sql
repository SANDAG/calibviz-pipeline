with abm3_temp as (
    select
        case
            when h.auto_ownership = 0 then '0: No Vehicles'
            when h.auto_ownership > h.num_adults then '2: Vehicles >= Adults'
            else '1: 1+ Veh/Adults > Veh'
        end as veh_ownership_category,
        coalesce(m.mode_hts, t.tour_mode) as tour_mode,
        coalesce(p.purpose_hts, t.primary_purpose) as purpose
    from {{ ref('stg_abm3_tours') }} as t
    left join {{ ref('mode_mapping') }} as m
        on t.tour_mode = m.mode_abm3
    left join {{ ref('purpose_mapping') }} as p
        on t.primary_purpose = p.purpose_abm3
    left join {{ ref('stg_abm3_households') }} as h
        on t.household_id = h.household_id
),

abm3_source as (
    select
        veh_ownership_category,
        tour_mode,
        purpose,
        count(*) as abm_tours
    from abm3_temp
    group by veh_ownership_category, tour_mode, purpose
),

survey_source as (
    select
        ownershipcategory as veh_ownership_category,
        tour_mode,
        purpose,
        freq as survey_tours
    {% if var('survey_name') == 'hts' %}
        from {{ ref('stg_hts_tourMode') }}
    {% else %}
        from {{ ref('int_tours_transit_survey') }}
    {% endif %}
),

survey_abm3_tour_mode_joined as (
    select
        coalesce(s.veh_ownership_category, h.veh_ownership_category)
            as veh_ownership_category,
        coalesce(s.tour_mode, h.tour_mode) as tour_mode,
        coalesce(s.purpose, h.purpose) as purpose,
        coalesce(s.abm_tours, 0) as abm_tours,
        coalesce(h.survey_tours, 0) as survey_tours
    from abm3_source as s
    full join survey_source as h
        on
            s.tour_mode = h.tour_mode
            and s.purpose = h.purpose
            and s.veh_ownership_category = h.veh_ownership_category
)

select * from survey_abm3_tour_mode_joined
