with long_format as (
    select
        scenario,
        source,
        metric,
        value
    from {{ ref('int_abm_hts_totals') }}
        unpivot (
            value for metric in (
                total_stops,
                total_participants,
                vmt,
                trips,
                households,
                population
            )
        )
)

select * from long_format
    pivot (
        MAX(value)
        for source in ('ABM', 'HTS')
    )
order by scenario, metric
