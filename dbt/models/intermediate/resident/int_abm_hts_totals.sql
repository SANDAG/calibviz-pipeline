WITH tours AS (
    SELECT
        'ABM' AS source,
        scenario,
        SUM(
            (
                CAST(SUBSTRING(stop_frequency, 1, 1) AS INTEGER)
                + CAST(SUBSTRING(stop_frequency, 6, 1) AS INTEGER)
            ) * number_of_participants
        ) AS total_stops,
        SUM(number_of_participants) AS total_participants
    FROM {{ ref('stg_abm3_tours') }}
    GROUP BY scenario
),

trips AS (
    SELECT
        'ABM' AS source,
        scenario,
        SUM(distance_drive * weight_trip) AS vmt,
        SUM(weight_person_trip) AS trips
    FROM {{ ref('stg_abm3_trips') }}
    GROUP BY scenario
),

households AS (
    SELECT
        'ABM' AS source,
        scenario,
        COUNT(DISTINCT household_id) AS households
    FROM {{ ref('stg_abm3_households') }}
    GROUP BY scenario
),

persons AS (
    SELECT
        'ABM' AS source,
        scenario,
        COUNT(DISTINCT person_id) AS population
    FROM {{ ref('stg_abm3_persons') }}
    GROUP BY scenario
),

abm AS (
    SELECT
        t.source,
        t.scenario,
        t.total_stops,
        t.total_participants,
        tr.vmt,
        tr.trips,
        h.households,
        p.population
    FROM tours AS t
    JOIN trips AS tr ON t.scenario = tr.scenario
    JOIN households AS h ON t.scenario = h.scenario
    JOIN persons AS p ON t.scenario = p.scenario
),

hts AS (
    SELECT
        'HTS' AS source,
        NULL as scenario,
        stops AS total_stops,
        tours AS total_participants,
        vmt,
        trips,
        households,
        population
    FROM {{ ref('stg_hts_totals') }}
        PIVOT (
            MAX(value)
            FOR variable IN (
                'Stops',
                'Tours',
                'VMT',
                'Trips',
                'Households',
                'Population'
            )
        )
)

SELECT * FROM abm
UNION ALL
SELECT * FROM hts
