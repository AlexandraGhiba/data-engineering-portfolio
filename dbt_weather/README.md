# Weather Data Pipeline

An end-to-end batch data engineering pipeline that retrieves hourly weather data from the Open-Meteo API, loads it into DuckDB using dlt, transforms and tests the data with dbt, and produces daily analytics-ready weather metrics.

## Architecture

```text
Open-Meteo API
       ↓
Python
       ↓
dlt
       ↓
DuckDB
       ↓
dbt Staging
       ↓
Daily Weather Mart
       ↓
Data Quality Tests
```

## Tech Stack

- **Python** — API extraction and pipeline execution
- **Open-Meteo API** — weather data source
- **dlt** — data ingestion and loading
- **DuckDB** — analytical storage
- **dbt Core** — transformations and data quality
- **dbt-duckdb** — DuckDB adapter for dbt

## Pipeline

The pipeline retrieves 30 days of hourly weather data from the Open-Meteo API for five Romanian cities:

- Bucharest
- Cluj-Napoca
- Iasi
- Timisoara
- Constanta

The following weather metrics are collected:

- temperature
- relative humidity
- wind speed
- precipitation
- cloud cover

dlt loads the raw weather data into DuckDB.

dbt then transforms the data through two analytical layers:

```text
Raw Weather Data
       ↓
stg_weather
       ↓
weather_daily
```

`stg_weather` creates a cleaned staging layer.

`weather_daily` aggregates hourly observations into daily weather metrics for each city.

## Data Quality

The pipeline validates the data before and during dbt processing.

Python validation checks:

- Data was successfully loaded
- All five cities are present
- Critical fields do not contain NULL values

dbt tests validate:

- Required fields are not NULL
- City/date combinations are unique
- Temperature values follow expected logical relationships

All dbt models and tests are executed through:

```bash
dbt build
```

## Key Engineering Features

- API data extraction
- 30-day hourly weather ingestion
- Multi-city data collection
- dlt ingestion pipeline
- DuckDB analytical storage
- dbt staging model
- Daily analytical mart
- Python data validation
- Automated dbt data-quality tests
- Reproducible pipeline execution

## Run Locally

Navigate to the project:

```powershell
cd E:\data-engineering-portfolio\dbt_weather
```

Run the complete pipeline:

```powershell
python weather_pipeline.py
```

The pipeline executes:

```text
Open-Meteo API
       ↓
dlt ingestion
       ↓
DuckDB
       ↓
Raw data validation
       ↓
dbt build
       ↓
dbt models + tests
```

A successful execution ends with output similar to:

```text
Rows: 3,600
Cities: 5
Critical NULLs: 0
DuckDB validation passed.

Completed successfully
dbt build passed.

Pipeline completed successfully!
```

The exact number of rows may vary depending on the data returned by the API.

## What This Project Demonstrates

This project demonstrates how API extraction, automated ingestion, analytical storage, SQL transformation, and data-quality testing can be combined into a reproducible end-to-end batch data engineering pipeline.