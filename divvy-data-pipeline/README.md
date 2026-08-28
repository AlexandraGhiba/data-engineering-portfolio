# 🚲 Divvy Bike-Share Data Pipeline

An end-to-end batch data engineering pipeline that processes Divvy bike-share trip data using **Apache Airflow, Python, Parquet, DuckDB and dbt**.

The project demonstrates monthly ingestion, incremental processing, SCD Type 2 station history, temporal foreign keys, data quality testing and analytical reporting.

## Architecture

```text
Divvy ZIP / CSV
      ↓
Apache Airflow
      ↓
Python ingestion
      ↓
Partitioned Parquet
      ↓
DuckDB
      ↓
dbt staging + intermediate
      ↓
SCD Type 2 station history
      ↓
dim_stations + fct_trips
      ↓
Analytical marts
      ↓
dbt tests
```

## Stack

| Layer | Tool |
|---|---|
| Ingestion | Python |
| Orchestration | Apache Airflow |
| Storage | Parquet + DuckDB |
| Transformation | dbt |
| Modeling | Fact/Dimension + SCD Type 2 |
| Data Quality | dbt Tests |
| Infrastructure | Docker |

## Dataset

The pipeline processes historical Divvy bike-share trips.

Current dataset:

| Month | Raw Trips |
|---|---:|
| January 2024 | 144,873 |
| February 2024 | 223,164 |
| March 2024 | 301,687 |
| **Total** | **669,724** |

After validation and duration filtering, `fct_trips` contains **669,493 trips with 669,493 distinct `ride_id` values**.

## Key Engineering Features

- Monthly parameterized ingestion with Airflow
- Parquet storage partitioned by year/month
- DuckDB analytical warehouse
- dbt staging, intermediate and mart layers
- Incremental `fct_trips` keyed by `ride_id`
- SCD Type 2 station history
- Time-aware station foreign keys
- Automated dbt data quality tests
- Idempotent monthly processing

## Station History — SCD Type 2

Station names and locations can change over time. In some cases, the same station ID appears at significantly different locations.

The project preserves historical station versions using **SCD Type 2** rather than assigning every historical trip to the latest station record.

```text
station_id
    ↓
monthly station observations
    ↓
dbt snapshot
    ↓
dim_stations
    ↓
historical station versions
```

`fct_trips` uses temporal foreign keys so each trip is linked to the station version that was valid when the trip occurred.

## Analytical Marts

### Station Imbalance

`mart_station_imbalance` identifies stations with the largest average weekday difference between departures and arrivals, separated by **member vs casual** riders.

Example:

```text
Streeter Dr & Grand Ave

Casual:  -4.90 net trips / weekday
Member:  +4.52 net trips / weekday
```

### Monthly Usage

`mart_monthly_usage` tracks trip volume, average duration and rider-type share.

Casual rider share increased across the available history:

```text
January:   16.9%
February:  21.1%
March:     27.4%
```

Casual riders also consistently recorded longer average trip durations than members.

### Station Identity Changes

`mart_station_changes` detects renamed, relocated and potential re-issued station IDs.

Example:

```text
station_id: 517

Public Rack - Pulaski Rd & Armitage Ave
                ↓
Clark St & Jarvis Ave

Movement: ~11.8 km
```

Without SCD Type 2 history, trips belonging to these different station versions could be incorrectly combined under the same station identity.

## Airflow DAG

The monthly workflow contains seven stages:

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

## Data Quality

The final dbt test suite produced:

```text
PASS  = 12
WARN  = 1
ERROR = 0
TOTAL = 13
```

The warning represents source trips with a missing `start_station_id` and is intentionally configured with warning severity.

Critical tests validate:

- unique and non-null `ride_id`
- accepted rider and bike types
- positive trip duration
- unique station versions
- fact-to-dimension relationships

## Project Structure

```text
divvy-data-pipeline/
├── dags/
│   └── ingest_dag.py
├── dbt_project/
│   ├── models/
│   │   ├── staging/
│   │   ├── intermediate/
│   │   └── marts/
│   ├── snapshots/
│   └── tests/
├── scripts/
├── raw/
├── docker-compose.yml
├── profiles.yml
└── README.md
```

## How to Run

Start the Docker environment:

```bash
docker compose up -d
```

Open Airflow:

```text
http://localhost:8080
```

Trigger:

```text
divvy_monthly_pipeline
```

and provide the processing `year` and `month`.

Monthly data should be processed chronologically to preserve correct SCD Type 2 station history.

Run dbt tests manually:

```bash
docker exec -it divvy_airflow dbt test \
  --project-dir /opt/airflow/dbt_project \
  --profiles-dir /opt/airflow \
  --vars "{processing_year: 2024, processing_month: 3}"
```

Stop the environment:

```bash
docker compose down
```

## What This Project Demonstrates

**Python · SQL · Airflow · Parquet · DuckDB · dbt · Docker · Incremental Loading · SCD Type 2 · Dimensional Modeling · Data Quality Testing**

## Author

**Ghiba Alexandra**

Data Engineering portfolio focused on building reliable and reproducible data pipelines.