# ENTSO-E Energy Price Pipeline

A small end-to-end data engineering project that extracts Romanian day-ahead electricity prices from the ENTSO-E Transparency Platform, loads them into DuckDB with dlt, transforms and validates them with dbt, and generates a daily analytical report.

The project demonstrates a reproducible local workflow using **Python, dlt, DuckDB, dbt and SQL**, with timezone-aware date handling, API retry logic, structured logging and basic execution metrics.

---

## Project Overview

The pipeline follows this flow:

```text
ENTSO-E API
    ↓
Python extraction + XML parsing
    ↓
Timezone-aware Romanian date handling
    ↓
dlt ingestion
    ↓
DuckDB raw layer
    ↓
dbt staging + data quality tests
    ↓
dbt daily mart
    ↓
Daily price report
```

The pipeline works with Romanian calendar dates using the `Europe/Bucharest` timezone.

ENTSO-E returns timestamps in UTC, so the requested Romanian day is converted to the correct UTC interval before the API request is sent.

Example:

```text
Romanian date:
2026-08-26

UTC API interval:
202608252100 -> 202608262100
```

The market data is normally provided at 15-minute resolution:

```text
24 hours × 4 observations/hour = 96 observations
```

---

## Technologies

- Python
- ENTSO-E Transparency Platform API
- dlt
- DuckDB
- dbt
- SQL
- Git / GitHub

---

## Project Structure

```text
entsoe_energy/
│
├── data/
│   └── energy.duckdb
│
├── dbt_energy/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   ├── stg_entsoe_prices.sql
│   │   │   └── stg_entsoe_prices.yml
│   │   │
│   │   └── marts/
│   │       └── daily_prices.sql
│   │
│   └── tests/
│       ├── no_duplicate_timestamps.sql
│       └── price_sanity_check.sql
│
├── src/
│   ├── entsoe_api.py
│   ├── dlt_pipeline.py
│   └── report.py
│
├── run_pipeline.py
├── dbt_project.yml
├── profiles.yml
├── requirements.txt
├── .gitignore
└── README.md
```

Generated folders, local databases, logs and secrets are excluded from Git.

---

## Pipeline Components

### 1. ENTSO-E API Extraction

`src/entsoe_api.py` is responsible for communication with the ENTSO-E Transparency Platform.

It:

- loads the API token from environment variables;
- calculates the correct UTC interval for a Romanian calendar day;
- requests Romanian day-ahead electricity prices;
- parses the XML response;
- supports both `PT15M` and `PT60M` ENTSO-E resolutions;
- keeps only observations belonging to the requested Romanian calendar date;
- returns timezone-aware timestamps.

### Retry and Exponential Backoff

Temporary API failures are handled explicitly.

The pipeline retries these HTTP status codes:

```text
429
500
502
503
504
```

The implementation performs up to five attempts and uses exponential backoff between retries:

```text
2s → 4s → 8s → 16s
```

If ENTSO-E returns a `Retry-After` header, the pipeline respects it.

This makes the extraction step more resilient to temporary server errors and API rate limiting.

---

### 2. Timezone-Aware Date Handling

Romania uses `Europe/Bucharest`, which is UTC+2 in winter and UTC+3 in summer.

Instead of hard-coding an offset, the pipeline creates the requested local-day boundaries and converts them to UTC before querying ENTSO-E.

This keeps the implementation correct when daylight-saving time changes.

Parsed UTC timestamps are converted back to Romanian local time when filtering observations for the requested date.

---

### 3. dlt Ingestion

`src/dlt_pipeline.py` defines the ingestion pipeline and loads parsed records into DuckDB.

The raw table is:

```text
raw.raw_entsoe_prices
```

Main fields:

```text
timestamp
price_eur_mwh
```

The dlt resource uses:

```text
write_disposition = merge
primary_key = timestamp
```

This makes the load idempotent: rerunning the same date does not create duplicate timestamp records.

Historical dates remain stored in DuckDB when newer dates are loaded.

---

### 4. Structured Logging and Basic Metrics

The Python ingestion layer uses the standard `logging` module instead of relying only on `print()` statements.

Example log events include:

```text
entsoe_ingestion_start
entsoe_response
entsoe_request_success
entsoe_temporary_error
entsoe_ingestion_metrics
dlt_load_complete
```

Logs contain timestamps, severity levels, component names and key-value information.

The pipeline also records two basic execution metrics:

```text
rows=96
duration_seconds=...
```

For example:

```text
entsoe_ingestion_metrics target_date=2026-09-02 rows=96 duration_seconds=0.78
```

This provides lightweight observability without introducing additional infrastructure such as Prometheus or Grafana.

---

### 5. DuckDB

DuckDB is used as the local analytical database.

The database is stored in:

```text
data/energy.duckdb
```

The main data flow inside DuckDB is:

```text
raw.raw_entsoe_prices
        ↓
main.stg_entsoe_prices
        ↓
main.daily_prices
```

DuckDB stores historical observations locally, so previously processed dates remain available after new pipeline runs.

The database file itself is treated as a local generated artifact and is not committed to Git.

---

### 6. dbt Transformation Layer

dbt is responsible for SQL transformations, documentation and data quality checks.

The project contains:

```text
staging model:
main.stg_entsoe_prices

daily mart:
main.daily_prices
```

#### Staging Model

`dbt_energy/models/staging/stg_entsoe_prices.sql` cleans the raw ENTSO-E observations and derives the Romanian price date.

Main fields include:

```text
timestamp
price_eur_mwh
price_date
```

#### Daily Mart

`dbt_energy/models/marts/daily_prices.sql` aggregates the 15-minute observations by date.

For each day it calculates:

```text
average price
minimum price
maximum price
number of observations
```

---

## Data Quality

The project uses dbt schema tests and custom SQL tests.

Checks include:

- timestamps are not null;
- prices are not null;
- timestamps are unique;
- duplicate timestamps are rejected;
- electricity prices remain within the configured sanity range.

A successful dbt build currently finishes with:

```text
PASS=7
WARN=0
ERROR=0
SKIP=0
```

For a normal Romanian day with 15-minute resolution, the pipeline expects:

```text
96 observations
```

The ingestion layer also logs a warning when the number of parsed rows differs from 96.

---

## Daily Price Report

`src/report.py` reads the transformed `main.daily_prices` table and prints a daily summary.

Example:

```text
DATE                 AVG PRICE      MIN PRICE      MAX PRICE   OBSERVATIONS
--------------------------------------------------------------------------------
2026-08-18              164.28         114.80         220.16             96
2026-08-19              167.65         123.35         224.07             96
2026-08-20              161.42          95.00         216.22             96
2026-08-21              169.56          55.98         229.78             96
2026-08-26              185.27         116.41         261.57             96
2026-09-02              197.88         100.64         336.59             96
```

The report shows all historical dates currently stored in DuckDB.

---

## Running the Pipeline

From the `entsoe_energy` project directory:

```powershell
python run_pipeline.py
```

When no date is provided, the pipeline processes yesterday according to the `Europe/Bucharest` timezone.

A specific Romanian calendar date can also be supplied:

```powershell
python run_pipeline.py 2026-08-26
```

The main runner executes:

```text
1. ENTSO-E ingestion
2. dbt build
3. Daily price report
```

A successful execution ends with:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

### Running from the Portfolio Root

If the repository is opened from the monorepo root:

```powershell
python entsoe_energy\run_pipeline.py
```

A specific date can be supplied in the same way:

```powershell
python entsoe_energy\run_pipeline.py 2026-08-26
```

---

## Security

The ENTSO-E API token is stored locally in a `.env` file.

Example:

```text
ENTSOE_API_TOKEN=your_api_token_here
```

The `.env` file must never be committed to GitHub.

Local/generated artifacts such as database files, logs, dbt build output and Python caches are also excluded from version control.

---

## Reliability Features

The project includes several production-minded improvements while keeping the architecture intentionally lightweight:

- timezone-aware Romanian date handling;
- explicit handling of HTTP `429` and retryable `5xx` errors;
- exponential retry backoff;
- support for the `Retry-After` response header;
- request and ingestion duration logging;
- row-count logging;
- warning on unexpected daily observation counts;
- idempotent dlt merge loading;
- dbt data quality tests.

---

## Project Goal

The goal of the project is to demonstrate a compact but complete data engineering workflow:

```text
Extract → Parse → Ingest → Store → Transform → Validate → Report
```

The project combines Python, dlt, DuckDB, dbt and SQL into a reproducible local pipeline for Romanian electricity market data.

It intentionally avoids unnecessary infrastructure while still demonstrating practical concerns such as API reliability, idempotency, data quality, observability and timezone correctness.

---

## What I Learned

This project helped me practice:

- working with a real external API;
- parsing XML data;
- handling UTC and Romanian local time correctly;
- accounting for daylight-saving time;
- implementing retry logic with exponential backoff;
- handling rate limiting and temporary API failures;
- using structured application logging;
- recording simple execution metrics;
- loading data with dlt;
- using merge semantics for idempotent ingestion;
- storing analytical data in DuckDB;
- building staging and mart models with dbt;
- writing data quality tests;
- preserving historical data without creating duplicates;
- running the complete workflow from one command.

---

## Example Successful Run

A complete successful execution includes:

```text
ENTSO-E ingestion
    ✓ API request successful
    ✓ 96 observations parsed
    ✓ dlt load completed

dbt build
    ✓ PASS=7
    ✓ WARN=0
    ✓ ERROR=0

Daily report
    ✓ historical daily prices generated

PIPELINE COMPLETED SUCCESSFULLY
```