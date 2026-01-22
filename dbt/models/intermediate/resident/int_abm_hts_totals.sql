WITH tours AS (
    SELECT
        'ABM' AS source,
        SUM(
            (
                CAST(SUBSTRING(stop_frequency, 1, 1) AS INTEGER)
                + CAST(SUBSTRING(stop_frequency, 6, 1) AS INTEGER)
            ) * number_of_participants
        ) AS total_stops,
        SUM(number_of_participants) AS total_participants
    FROM {{ ref('stg_abm3_tours') }}
),

trips AS (
    SELECT
        'ABM' AS source,
        SUM(distance_drive * weight_trip) AS vmt,
        SUM(weight_person_trip) AS trips
    FROM {{ ref('stg_abm3_trips') }}
),

households AS (
    SELECT
        'ABM' AS source,
        COUNT(DISTINCT household_id) AS households
    FROM {{ ref('stg_abm3_households') }}
),

persons AS (
    SELECT
        'ABM' AS source,
        COUNT(DISTINCT person_id) AS population
    FROM {{ ref('stg_abm3_persons') }}
),

abm AS (
    SELECT
        t.source,
        t.total_stops,
        t.total_participants,
        tr.vmt,
        tr.trips,
        h.households,
        p.population
    FROM tours AS t
    CROSS JOIN trips AS tr
    CROSS JOIN households AS h
    CROSS JOIN persons AS p
),

hts AS (
    SELECT
        'HTS' AS source,
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
