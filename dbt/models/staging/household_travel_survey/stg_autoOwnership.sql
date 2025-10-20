-- with source as (SELECT * FROM {{ source('hts', 'autoOwnership') }})

-- SELECT 
--   *
-- FROM source

with source as (
    SELECT 
        (* EXCLUDE filename),
        split_part(
            split_part(filename, '/abm_runs_v2//', 2),
            '/src/asim/visualizer/visualizer/hts_2022',
            1
        ) as scenario_id
    FROM read_csv_auto(
        {{ get_scenario_paths('autoOwnership', 'src/asim/visualizer/visualizer/hts_2022') }},
        filename=true,
        union_by_name=true
    )
)

SELECT * FROM source