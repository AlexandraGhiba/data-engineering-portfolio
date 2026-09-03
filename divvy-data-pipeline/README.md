# 🚲 Divvy Bike-Share Data Pipeline

End-to-end batch data engineering pipeline for historical Divvy bike-share data using **Apache Airflow, Python, Parquet, DuckDB, dbt, and Docker**.

The project demonstrates monthly ingestion, incremental processing, dimensional modeling, **SCD Type 2 station history**, temporal foreign keys, and automated data quality testing.

## Architecture

```text
Divvy CSV
    ↓
Airflow
    ↓
Python ingestion
    ↓
Partitioned Parquet
    ↓
DuckDB
    ↓
dbt transformations
    ↓
SCD Type 2
    ↓
dim_stations + fct_trips
    ↓
Analytical marts
    ↓
dbt tests
```

## Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | Python |
| Orchestration | Apache Airflow |
| Storage | Parquet + DuckDB |
| Transformation | dbt |
| Modeling | Fact/Dimension + SCD Type 2 |
| Data Quality | dbt Tests |
| Infrastructure | Docker |

## Dataset

The pipeline processes Divvy bike-share trips from **January–March 2024**.

| Month | Raw Trips |
|---|---:|
| January | 144,873 |
| February | 223,164 |
| March | 301,687 |
| **Total** | **669,724** |

After validation and filtering, `fct_trips` contains **669,493 valid trips**.

## Key Engineering Features

- Monthly Airflow-orchestrated ingestion
- Year/month partitioned Parquet storage
- DuckDB analytical warehouse
- dbt staging, intermediate, dimension, fact, and mart layers
- Incremental `fct_trips` keyed by `ride_id`
- SCD Type 2 station history
- Temporal station foreign keys
- Automated dbt data quality tests
- Idempotent monthly processing

## Airflow DAG

```text
ingest_month
      ↓
load_duckdb
      ↓
build_staging_and_intermediate
      ↓
build_station_current
      ↓
run_station_snapshot
      ↓
build_fact_and_marts
      ↓
run_dbt_tests
```

Airflow orchestrates the complete workflow and ensures each stage runs only after its upstream dependencies succeed.

## SCD Type 2 Station History

Station metadata can change over time through renames, relocations, or station ID reuse.

The pipeline uses a **dbt snapshot and SCD Type 2 dimension** to preserve historical station versions instead of overwriting previous values.

`fct_trips` uses temporal foreign keys:

```text
start_station_version_key
end_station_version_key
```

This links each trip to the station version that was valid when the trip occurred.

## Analytical Marts

### Monthly Usage

`mart_monthly_usage` tracks trip volume, average duration, and rider-type share.

| Month | Rider | Trips | Avg. Duration | Share |
|---|---|---:|---:|---:|
| Jan | Casual | 24,446 | 21.32 min | 16.9% |
| Jan | Member | 120,330 | 13.80 min | 83.1% |
| Feb | Casual | 47,157 | 25.19 min | 21.1% |
| Feb | Member | 175,979 | 12.92 min | 78.9% |
| Mar | Casual | 82,500 | 24.97 min | 27.4% |
| Mar | Member | 219,081 | 11.97 min | 72.6% |

Casual rider share increased from **16.9% to 27.4%**, while casual riders consistently had longer average trip durations.

### Station Changes

`mart_station_changes` detects station renames, relocations, and potential station ID reuse.

The current dataset contains **14 detected station changes**.

### Station Imbalance

`mart_station_imbalance` compares weekday departures and arrivals by station and rider type, producing **4,562 analytical records**.

## Final Models

| Model | Rows |
|---|---:|
| `fct_trips` | 669,493 |
| `dim_stations` | 2,796 |
| `stations_snapshot` | 2,796 |
| `mart_monthly_usage` | 6 |
| `mart_station_changes` | 14 |
| `mart_station_imbalance` | 4,562 |

## Data Quality

Final dbt test results:

```text
PASS  = 12
WARN  = 1
ERROR = 0
TOTAL = 13
```

Tests validate:

- unique and non-null `ride_id`
- accepted rider and bike types
- positive trip duration
- unique station versions
- fact-to-dimension relationships

The single warning represents source records with a missing `start_station_id` and is intentionally configured with warning severity.

## Project Structure

```text
divvy-data-pipeline/
├── dags/
│   └── ingest_dag.py
├── dbt_project/
│   ├── models/
│   ├── snapshots/
│   └── tests/
├── scripts/
├── inspect_results.py
├── docker-compose.yml
├── profiles.yml
└── README.md
```

## How to Run

Start the environment:

```bash
docker compose up -d
```

Open Airflow at:

```text
http://localhost:8080
```

Trigger:

```text
divvy_monthly_pipeline
```

After all seven tasks complete successfully, inspect the final DuckDB models:

```bash
python inspect_results.py
```

Stop the environment:

```bash
docker compose down
```

## What This Project Demonstrates

**Python · SQL · Airflow · Parquet · DuckDB · dbt · Docker · Incremental Loading · SCD Type 2 · Temporal Joins · Dimensional Modeling · Data Quality Testing**

## Author

**Ghiba Alexandra**