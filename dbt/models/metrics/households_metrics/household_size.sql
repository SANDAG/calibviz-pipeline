-- Calculate household size distribution as a share of total households
-- Exclude group quarters (e.g., large institutions, dorms) from source staging (where unittype = 0)
-- Cap household sizes at 5+ for comparison with survey data

with abm3_hhsize_capped as (
    select 
        case 
            when hhsize > 5 then 5 
            else hhsize 
        end as hhsize,
        count(*) as household_count
    from {{ ref('stg_abm3_households') }} 
    where unittype = 0 -- exclude group quarters
    group by 
        case 
            when hhsize > 5 then 5 
            else hhsize 
        end
),

abm3_source as (
    select 
        hhsize,
        household_count,
        household_count * 1.0 / sum(household_count) over () as proportion
    from abm3_hhsize_capped
),

hts_source as (
    select 
        hhsize, 
        FREQ * 1.0 / sum(FREQ) over () as proportion 
    from {{ ref('stg_hts_hhsizeDist') }}
),

hts_abm3_joined as (
    select 
        a.hhsize, 
        a.proportion as abm_proportion, 
        h.proportion as hts_proportion
    from abm3_source a
    join hts_source h on a.hhsize = h.hhsize
)

select * from hts_abm3_joined
order by hhsize
