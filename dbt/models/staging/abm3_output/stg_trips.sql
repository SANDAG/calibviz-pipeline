-- with source as (SELECT * FROM {{ source('abm3_resident_output', 'final_trips') }})

-- SELECT * FROM source


with source as (
    SELECT 
        *,
        split_part(
            split_part(filename, 'abm_runs_v2/', 2),
            '/output',
            1
        ) as scenario_id
    FROM read_csv_auto(
        {{ get_scenario_paths('final_trips', 'output/resident') }},
        filename=true,
        union_by_name=true
    )
)

SELECT * FROM source