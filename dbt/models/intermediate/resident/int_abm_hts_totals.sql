-- Intermediate model that calculates all base metrics for both ABM and HTS
-- This serves as the foundation for multiple downstream mart models

with abm_metrics as (
    select
        'ABM' as data_source,
        (
            select count(distinct household_id)
            from {{ ref('stg_abm3_households') }}
        ) as households,
        (select count(distinct person_id) from {{ ref('stg_abm3_persons') }}
        ) as population,
        (select sum(number_of_participants) from {{ ref('stg_abm3_tours') }}
        ) as tours,
        (select sum(weight_person_trip) from {{ ref('stg_abm3_trips') }}
        ) as trips,
        (select sum(
            (
                cast(substring(stop_frequency, 1, 1) as integer)
                + cast(substring(stop_frequency, 6, 1) as integer)
            )
            * number_of_participants
        ) from {{ ref('stg_abm3_tours') }}) as stops,
        (
            select sum(distance_drive * weight_trip)
            from {{ ref('stg_abm3_trips') }}
        ) as vmt
),

hts_metrics as (
    select
        'HTS' as data_source,
        max(case when variable = 'Households' then value end) as households,
        max(case when variable = 'Population' then value end) as population,
        max(case when variable = 'Tours' then value end) as tours,
        max(case when variable = 'Trips' then value end) as trips,
        max(case when variable = 'Stops' then value end) as stops,
        max(case when variable = 'VMT' then value end) as vmt
    from {{ ref('stg_hts_totals') }}
)

select * from abm_metrics
union all
select * from hts_metrics
