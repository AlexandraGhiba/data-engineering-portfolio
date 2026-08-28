# Weather Data Pipeline — Python, dlt, DuckDB & dbt

An end-to-end weather data pipeline built with **Python, dlt, DuckDB, and dbt**.

The pipeline retrieves 30 days of hourly weather data from the **Open-Meteo API** for five Romanian cities, loads the data into DuckDB using dlt, transforms it with dbt, and validates the resulting data using automated data quality tests.

---

## Project Overview

This project demonstrates a complete modern data engineering workflow:

```text
Open-Meteo API
      │
      ▼
   Python
      │
      ▼
 dlt ingestion
      │
      ▼
   DuckDB
      │
      ├── Raw weather data
      │
      ▼
 dbt staging
      │
      ▼
dbt daily mart
      │
      ▼
Data quality tests
```

The pipeline collects hourly weather observations for:

* Bucharest
* Cluj-Napoca
* Iasi
* Timisoara
* Constanta

The following weather metrics are retrieved:

* Temperature
* Relative humidity
* Wind speed
* Precipitation
* Cloud cover

---

## Tech Stack

* **Python** — pipeline orchestration and API extraction
* **Open-Meteo API** — weather data source
* **dlt** — data ingestion and loading
* **DuckDB** — local analytical database
* **dbt Core** — data transformation and testing
* **dbt-duckdb** — DuckDB adapter for dbt

---

## Pipeline

The pipeline is orchestrated by `weather_pipeline.py` and consists of the following steps:

1. Extract 30 days of hourly weather data from the Open-Meteo API.
2. Load the raw data into DuckDB using dlt.
3. Validate the raw dataset using Python and SQL checks.
4. Run `dbt build` to create the transformation models.
5. Execute dbt data quality tests.

The pipeline checks that:

* Data was successfully loaded.
* All five cities are present.
* Critical fields do not contain NULL values.
* dbt models build successfully.
* dbt data quality tests pass.

---

## Project Structure

```text
dbt_weather/
│
├── analyses/
├── macros/
├── models/
├── seeds/
├── snapshots/
├── tests/
│
├── .gitignore
├── dbt_project.yml
├── profiles.yml
├── requirements.txt
├── weather_pipeline.py
└── README.md
```

Generated files and local environments such as `.venv/`, `target/`, `logs/`, and `*.duckdb` are excluded from version control.

---

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd dbt_weather
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

The project dependencies include:

```text
dlt[duckdb]
duckdb
dbt-core
dbt-duckdb
```

### 5. Verify dbt

```bash
dbt --version
```

The `dbt` executable is resolved from the active environment, so no machine-specific or user-specific path to `dbt.exe` is required.

---

## Running the Pipeline

With the virtual environment activated, run:

```bash
python weather_pipeline.py
```

The script executes the complete workflow:

```text
Open-Meteo API
      ↓
dlt
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

---

## dbt Models

The dbt project transforms the raw weather data in two stages.

### `stg_weather`

Creates a cleaned staging layer from the raw weather data loaded by dlt.

### `weather_daily`

Aggregates hourly observations into daily weather metrics for each city.

The resulting model can be used for analytical queries and further reporting.

---

## Data Quality

Data quality is checked at two levels.

### Python validation

Before dbt runs, the pipeline verifies:

* The DuckDB table contains data.
* All expected cities are present.
* Critical columns do not contain NULL values.

### dbt tests

dbt tests validate the transformed datasets, including:

* Required fields are not NULL.
* Daily city/date combinations are unique.
* Temperature values follow the expected logical relationships.

All transformations and tests are executed through:

```bash
dbt build
```

---

## Reproducibility

The project is designed to run without machine-specific configuration.

Python dependencies are defined in:

```text
requirements.txt
```

The dbt DuckDB database uses a relative path in `profiles.yml`, and the `dbt` executable is discovered from the active Python environment.

This allows another user to reproduce the project by creating a new virtual environment and installing the declared dependencies.

---

## Data Source

Weather data is provided by the **Open-Meteo API**.

The pipeline requests 30 days of hourly historical weather data using the coordinates of the five selected Romanian cities.
