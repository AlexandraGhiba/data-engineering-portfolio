import duckdb

DB_PATH = "warehouse.duckdb"

con = duckdb.connect(DB_PATH, read_only=True)

print("\n" + "=" * 70)
print("DIVVY DATA PIPELINE - RESULTS")
print("=" * 70)

# 1. Pipeline summary
print("\n[1] PIPELINE SUMMARY\n")

summary = con.sql("""
    SELECT
        COUNT(*) AS total_trips,
        COUNT(DISTINCT start_station_id) AS start_stations,
        COUNT(DISTINCT end_station_id) AS end_stations,
        ROUND(AVG(trip_duration_minutes), 2) AS avg_duration_min
    FROM fct_trips
""").df()

print(summary.to_string(index=False))


# 2. Monthly usage
print("\n" + "-" * 70)
print("[2] MONTHLY USAGE")
print("-" * 70 + "\n")

monthly = con.sql("""
    SELECT
        STRFTIME(trip_month, '%Y-%m') AS month,
        member_casual AS rider_type,
        trip_count,
        ROUND(avg_trip_duration_minutes, 2) AS avg_duration_min,
        ROUND(rider_type_share * 100, 1) AS share_pct
    FROM mart_monthly_usage
    ORDER BY trip_month, member_casual
""").df()

print(monthly.to_string(index=False))


# 3. Fact table sample
print("\n" + "-" * 70)
print("[3] FACT TRIPS - SAMPLE")
print("-" * 70 + "\n")

fact_sample = con.sql("""
    SELECT
        ride_id,
        rideable_type AS bike_type,
        STRFTIME(started_at, '%Y-%m-%d %H:%M') AS started,
        start_station_name AS start_station,
        end_station_name AS end_station,
        member_casual AS rider_type,
        ROUND(trip_duration_minutes, 2) AS duration_min
    FROM fct_trips
    ORDER BY started_at
    LIMIT 10
""").df()

print(fact_sample.to_string(index=False))


# 4. Station dimension sample
print("\n" + "-" * 70)
print("[4] STATION DIMENSION - SAMPLE")
print("-" * 70 + "\n")

stations = con.sql("""
    SELECT
        station_id,
        station_name,
        ROUND(latitude, 5) AS latitude,
        ROUND(longitude, 5) AS longitude,
        valid_from,
        valid_to
    FROM dim_stations
    ORDER BY station_name
    LIMIT 10
""").df()

print(stations.to_string(index=False))


## 5. Physical table row counts
print("\n" + "-" * 70)
print("[5] PHYSICAL MODEL ROW COUNTS")
print("-" * 70 + "\n")

physical_tables = con.sql("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'main'
      AND table_type = 'BASE TABLE'
    ORDER BY table_name
""").df()

rows = []

for table_name in physical_tables["table_name"]:
    count = con.sql(
        f'SELECT COUNT(*) AS row_count FROM "{table_name}"'
    ).fetchone()[0]

    rows.append({
        "model": table_name,
        "row_count": count
    })

import pandas as pd

counts = pd.DataFrame(rows)

print(counts.to_string(index=False))

con.close()

print("\n" + "=" * 70)
print("DONE")
print("=" * 70 + "\n")