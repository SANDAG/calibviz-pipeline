import duckdb

conn = duckdb.connect('resident_calibration.duckdb', read_only=True)

print("=== Arrival modes in stg_departing_trips_mode ===")
result = conn.execute("""
    SELECT DISTINCT arrival_mode 
    FROM calibration_staging.stg_departing_trips_mode 
    ORDER BY arrival_mode
""").fetchall()

for row in result:
    print(row[0])

print("\n=== Values with hotel_shuttle in tour_share_by_mode ===")
sample = conn.execute("""
    SELECT dimension_value, tour_type, level, survey_trip, model_trip
    FROM calibration_metrics.tour_share_by_mode 
    WHERE dimension = 'arrival_mode' AND dimension_value = 'hotel_shuttle'
""").fetchall()

for row in sample:
    print(row)

conn.close()
