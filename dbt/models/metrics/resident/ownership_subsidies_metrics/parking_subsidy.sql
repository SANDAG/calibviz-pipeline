with abm3_source as (
    select
        person_type,
        SUM(free_parking_weight) as validated
    from {{ ref('int_ownership_subsidy') }}
    where daily_parking_expenditure > 0 and (is_student or is_worker)
    group by person_type
    order by person_type
),

hts_source as (
    select
        pertype as person_type,
        free_parking_at_work as proportion
    from {{ ref('stg_hts_ownershipSubsidies') }}
),

hts_abm3_joined as (
    select
        a.person_type,
        a.validated as abm_proportion,
        h.proportion as hts_proportion
    from abm3_source as a
    inner join hts_source as h on a.person_type = h.person_type
)

select * from hts_abm3_joined
