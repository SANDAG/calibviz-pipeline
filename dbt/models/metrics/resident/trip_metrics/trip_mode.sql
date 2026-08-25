with abm3_temp as (
    select 
        trips.scenario,
        coalesce(m1.mode_hts, trips.trip_mode) as trip_mode,
        coalesce(m2.mode_hts, tours.tour_mode) as tour_mode,
        coalesce(purp.individual_category, tours.primary_purpose) as tour_purpose,
        trips.weight_person_trip
    from {{ ref('stg_abm3_trips') }} as trips
    left join {{ ref('mode_mapping') }} as m1
    on trips.trip_mode = m1.mode_abm3
    left join {{ ref('stg_abm3_tours') }} as tours
    on trips.tour_id = tours.tour_id and trips.scenario = tours.scenario
    left join {{ ref('mode_mapping') }} as m2
    on tours.tour_mode = m2.mode_abm3
    left join {{ ref('purpose_mapping') }} as purp
    on tours.primary_purpose = purp.purpose_abm3
),
abm3_source as (
    select 
        scenario,
        trip_mode,
        tour_mode,
        tour_purpose,
        sum(weight_person_trip) as abm_trips
    from abm3_temp as t
    group by scenario, trip_mode, tour_mode, tour_purpose
),
survey_source as (
    select
        trip_mode,
        tour_mode,
        purpose	as tour_purpose, 
        value as survey_trips
    {% if var('survey_name') == 'hts' %}
    from {{ ref('stg_hts_tripMode') }} as t
    {% else %}
    from {{ ref('int_trips_transit_survey') }} as t
    {% endif %}
),
survey_abm3_trip_mode_joined as (
    select 
        s.scenario,
        coalesce(s.trip_mode, h.trip_mode) as trip_mode,
        coalesce(s.tour_mode, h.tour_mode) as tour_mode,
        coalesce(s.tour_purpose, h.tour_purpose) as tour_purpose,
        coalesce(s.abm_trips, 0) as abm_trips, 
        coalesce(h.survey_trips, 0) as survey_trips
    from abm3_source s
    full join survey_source h
    on s.trip_mode = h.trip_mode
    and s.tour_mode = h.tour_mode
    and s.tour_purpose = h.tour_purpose
)

select * from survey_abm3_trip_mode_joined