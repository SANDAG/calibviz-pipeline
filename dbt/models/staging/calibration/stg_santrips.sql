with survey_source as (
    SELECT * FROM {{ ref('stg_tripcount_mode') }} 
),

standardized as (
    select
        -- trip identifiers
        trip_id,
        tour_id,
        person_id,
        
        -- classification
        tour_type,
        case 
            when tour_type like 'res_%' then 'resident'
            when tour_type like 'vis_%' then 'visitor'
            when tour_type like 'emp%' then 'employee'
            else tour_type
        end as tour_type_general,
        
        -- mode mapping
        COALESCE(m.mapped_mode, s.arrival_mode) as mapped_mode,
        
        -- geography
        origin_pmsa,
        
        -- weights
        weight_person_trip as trip,
        
        -- metadata
        'survey' as data_source,
        current_timestamp() as processed_at
    from survey_source s
    LEFT JOIN {{ ref('arrival_mode_mapping') }} m
    ON s.arrival_mode = m.arrival_mode
    {% if var('exclude_employee', false) %}
    -- Exclude employee trips
    where tour_type != 'emp'
    {% else %}
    -- Include employee trips (default behavior)
    where tour_type = 'emp'
    {% endif %}
)

select * from standardized
    