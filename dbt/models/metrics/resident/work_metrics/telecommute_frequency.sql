-- Calculate telecommute frequency
with abm3_source as (
    select
    persons.scenario,
    tm.telecommute_hts as telecommute_frequency, 
    count(*) as freq, 
    count(*) * 1.0 / sum(count(*)) over (partition by persons.scenario) as proportion
    from {{ ref('stg_abm3_persons') }} as persons
    left join {{ ref('stg_abm3_households') }} as households
    on persons.household_id = households.household_id and persons.scenario = households.scenario
    left join {{ ref('telecommute_mapping') }} as tm
    on persons.telecommute_frequency = tm.telecommute_abm3
    where persons.is_out_of_home_worker = TRUE and 
    {{ include_gq_where('households.unittype') }}  -- -> will be "households.unittype = 0" if include_gq is false
    group by persons.scenario, tm.telecommute_hts
),

hts_source as (
    select 
        telecommute_frequency,
        round(freq, 0) as freq,
        freq * 1.0 / sum(freq) over () as proportion
    from {{ ref('stg_hts_telecommuteFrequency') }}
),

hts_abm3_joined as (
    select 
        a.scenario,
        coalesce(a.telecommute_frequency, h.telecommute_frequency) as telecommute_frequency, 
        round(a.proportion, 4) as abm_proportion,
        round(h.proportion, 4) as hts_proportion
    from abm3_source a
    full join hts_source h
    on a.telecommute_frequency = h.telecommute_frequency
)

select * from hts_abm3_joined
order by scenario, telecommute_frequency
