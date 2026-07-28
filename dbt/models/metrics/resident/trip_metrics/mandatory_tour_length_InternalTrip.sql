with abm3_persons_with_district as (
    select
        p.person_id,
        p.ptype,
        p.workplace_zone_id,
        p.school_zone_id,
        p.work_from_home,
        p.is_internal_worker,
        p.distance_to_work,
        p.distance_to_school,
        geo.pseudomsa as home_district
    from {{ source('abm3_resident_output', 'final_persons') }} as p
    left join {{ ref('mgra_taz_pmsa_xref') }} as geo
        on p.home_zone_id = geo.mgra
),

abm3_work as (
    select
        home_district,
        'Work' as purpose,
        avg(distance_to_work) as avg_distance
    from abm3_persons_with_district
    where
        workplace_zone_id > 0
        and work_from_home = false
        and is_internal_worker = true
    group by home_district
),

abm3_university as (
    select
        home_district,
        'University' as purpose,
        avg(distance_to_school) as avg_distance
    from abm3_persons_with_district
    where
        ptype = 3
        and school_zone_id > 0
    group by home_district
),

abm3_school as (
    select
        home_district,
        'School' as purpose,
        avg(distance_to_school) as avg_distance
    from abm3_persons_with_district
    where
        ptype >= 6
        and school_zone_id > 0
    group by home_district
),

abm3_all as (
    select * from abm3_work
    union all
    select * from abm3_university
    union all
    select * from abm3_school
),

-- Calculate totals directly from raw person data (not average of averages)
abm3_work_total as (
    select
        null as home_district,
        'Work' as purpose,
        avg(distance_to_work) as avg_distance
    from abm3_persons_with_district
    where
        workplace_zone_id > 0
        and work_from_home = false
        and is_internal_worker = true
),

abm3_university_total as (
    select
        null as home_district,
        'University' as purpose,
        avg(distance_to_school) as avg_distance
    from abm3_persons_with_district
    where
        ptype = 3
        and school_zone_id > 0
),

abm3_school_total as (
    select
        null as home_district,
        'School' as purpose,
        avg(distance_to_school) as avg_distance
    from abm3_persons_with_district
    where
        ptype >= 6
        and school_zone_id > 0
),

abm3_with_totals as (
    select
        home_district,
        purpose,
        avg_distance
    from abm3_all
    union all
    select * from abm3_work_total
    union all
    select * from abm3_university_total
    union all
    select * from abm3_school_total
),

abm3_source as (
    select
        coalesce(d.pmsa_name, 'Total') as district,
        purpose,
        avg_distance as abm_avg_distance
    from abm3_with_totals as a
    left join {{ ref('pmsa_name') }} as d
        on a.home_district = d.pmsa_id
),

hts_source as (
    select
        "District" as district,
        purpose,
        value as hts_avg_distance
    from {{ source('hts', 'mandTripLengths') }}
),

joined as (
    select
        coalesce(a.district, h.district) as district,
        coalesce(a.purpose, h.purpose) as purpose,
        coalesce(a.abm_avg_distance, 0) as abm_avg_distance,
        coalesce(h.hts_avg_distance, 0) as hts_avg_distance
    from abm3_source as a
    full join hts_source as h
        on a.district = h.district
        and a.purpose = h.purpose
)

select * from joined
order by purpose, district
