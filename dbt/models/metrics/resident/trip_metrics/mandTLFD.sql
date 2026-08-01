-- Mandatory Tour Length Frequency Distribution
-- Calculates distribution of distances to work/school/university by home district and distance bin
-- Follows logic from Data Pipeline Tool: config/expressions.csv lines 39-41

with persons_with_district as (
    select
        p.scenario,
        p.person_id,
        p.ptype,
        p.workplace_zone_id,
        p.school_zone_id,
        p.work_from_home,
        p.is_internal_worker,
        p.distance_to_work,
        p.distance_to_school,
        case geo.pseudomsa
            when 1 then '1: Downtown'
            when 2 then '2: Central'
            when 3 then '3: North City'
            when 4 then '4: South Suburban'
            when 5 then '5: East Suburban'
            when 6 then '6: North County West'
            when 7 then '7: North County East'
            when 8 then '8: East County'
            else cast(geo.pseudomsa as varchar)
        end as home_district
    from {{ ref('stg_abm3_persons') }} as p
    left join {{ ref('mgra_taz_pmsa_xref') }} as geo
        on p.home_zone_id = geo.mgra
),

-- Create distance bins (1-mile increments, bins 1-51)
work_binned as (
    select
        scenario,
        person_id,
        home_district,
        'Work' as purpose,
        case
            when distance_to_work <= 0 then 0
            when distance_to_work >= 50 then 51
            else cast(floor(distance_to_work) + 1 as integer)
        end as distbin,
        1 as person_weight
    from persons_with_district
    where
        work_from_home = false
        and workplace_zone_id > 0
        and distance_to_work > 0
        and is_internal_worker = true
),

university_binned as (
    select
        scenario,
        person_id,
        home_district,
        'University' as purpose,
        case
            when distance_to_school <= 0 then 0
            when distance_to_school >= 50 then 51
            else cast(floor(distance_to_school) + 1 as integer)
        end as distbin,
        1 as person_weight
    from persons_with_district
    where
        ptype = 3  -- University students
        and school_zone_id > 0
        and distance_to_school > 0
),

school_binned as (
    select
        scenario,
        person_id,
        home_district,
        'School' as purpose,
        case
            when distance_to_school <= 0 then 0
            when distance_to_school >= 50 then 51
            else cast(floor(distance_to_school) + 1 as integer)
        end as distbin,
        1 as person_weight
    from persons_with_district
    where
        ptype >= 6  -- School age children
        and school_zone_id > 0
        and distance_to_school > 0
),

-- Union all purposes
all_purposes as (
    select * from work_binned
    union all
    select * from university_binned
    union all
    select * from school_binned
),

-- Aggregate by scenario, district, purpose, and distance bin
abm_aggregated as (
    select
        scenario,
        distbin,
        home_district as district,
        purpose,
        sum(person_weight) as abm_value
    from all_purposes
    group by scenario, distbin, home_district, purpose
),

-- Get HTS 2022 survey data
hts_2022_data as (
    select
        distbin,
        district,
        purpose,
        value as hts_2022_value
    from {{ ref('stg_hts_mandTLFD') }}
),

-- Get HTS 2023 survey data
hts_2023_data as (
    select
        distbin,
        district,
        purpose,
        value as hts_2023_value
    from {{ ref('stg_hts_2023_mandTLFD') }}
),

-- Join ABM and HTS data
final_comparison as (
    select
        a.scenario,
        coalesce(a.distbin, h22.distbin, h23.distbin) as distbin,
        coalesce(a.district, h22.district, h23.district) as district,
        coalesce(a.purpose, h22.purpose, h23.purpose) as purpose,
        a.abm_value,
        h22.hts_2022_value,
        h23.hts_2023_value
    from abm_aggregated a
    full outer join hts_2022_data h22
        on a.distbin = h22.distbin
        and a.district = h22.district
        and a.purpose = h22.purpose
    full outer join hts_2023_data h23
        on coalesce(a.distbin, h22.distbin) = h23.distbin
        and coalesce(a.district, h22.district) = h23.district
        and coalesce(a.purpose, h22.purpose) = h23.purpose
)

select
    scenario,
    distbin,
    district,
    purpose,
    coalesce(abm_value, 0) as abm_value,
    coalesce(hts_2022_value, 0) as hts_2022_value,
    coalesce(hts_2023_value, 0) as hts_2023_value
from final_comparison
order by scenario, district, purpose, distbin
