-- Overview comparison table showing raw metrics side by side
-- Variables include: Households, Population, Stops, Tours, Trips, VMT

with metrics_pivoted as (
    select
        data_source,
        households,
        population,
        stops,
        tours,
        trips,
        vmt
    from {{ ref('int_abm_hts_totals') }}
)

select
    'Households' as variables,
    max(case when data_source = 'HTS' then households end) as hts,
    max(case when data_source = 'ABM' then households end)
        as abm
from metrics_pivoted

union all

select
    'Population' as variables,
    max(case when data_source = 'HTS' then population end) as hts,
    max(case when data_source = 'ABM' then population end)
        as abm
from metrics_pivoted

union all

select
    'Stops' as variables,
    max(case when data_source = 'HTS' then stops end) as hts,
    max(case when data_source = 'ABM' then stops end)
        as abm
from metrics_pivoted

union all

select
    'Tours' as variables,
    max(case when data_source = 'HTS' then tours end) as hts,
    max(case when data_source = 'ABM' then tours end)
        as abm
from metrics_pivoted

union all

select
    'Trips' as variables,
    max(case when data_source = 'HTS' then trips end) as hts,
    max(case when data_source = 'ABM' then trips end)
        as abm
from metrics_pivoted

union all

select
    'VMT' as variables,
    max(case when data_source = 'HTS' then vmt end) as hts,
    max(case when data_source = 'ABM' then vmt end) as abm
from metrics_pivoted
