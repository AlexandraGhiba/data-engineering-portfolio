# ENTSO-E Energy Price Pipeline

An end-to-end data engineering project that extracts Romanian day-ahead electricity prices from the ENTSO-E Transparency Platform, loads them into DuckDB with dlt, transforms and validates them with dbt, and generates a daily analytical report.

The project demonstrates **Python, dlt, DuckDB, dbt and SQL**, with timezone-aware date handling, resilient API extraction, idempotent loading, data quality checks and application logging.

---

## Architecture

```text
ENTSO-E API
    ↓
Python extraction + XML parsing
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

The pipeline works with Romanian calendar dates using `Europe/Bucharest`. ENTSO-E uses UTC intervals, so the requested local day is converted to the correct UTC boundaries before the API request.

A normal 24-hour day at 15-minute resolution contains **96 observations**.

---

## Tech Stack

- **Python** — API integration, XML parsing, timezone handling and orchestration
- **ENTSO-E Transparency Platform API** — Romanian day-ahead electricity prices
- **dlt** — ingestion and merge loading
- **DuckDB** — local analytical database
- **dbt** — SQL transformations and data quality tests
- **SQL** — staging and analytical models
- **Git / GitHub** — version control

---

## Project Structure

```text
entsoe_energy/
├── data/
│   └── energy.duckdb
├── dbt_energy/
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml
│   │   │   ├── stg_entsoe_prices.sql
│   │   │   └── stg_entsoe_prices.yml
│   │   └── marts/
│   │       └── daily_prices.sql
│   └── tests/
│       ├── no_duplicate_timestamps.sql
│       └── price_sanity_check.sql
├── src/
│   ├── entsoe_api.py
│   ├── dlt_pipeline.py
│   └── report.py
├── run_pipeline.py
├── dbt_project.yml
├── profiles.yml
├── requirements.txt
├── .gitignore
└── README.md
```

Generated data, DuckDB files, logs, dbt build artifacts and secrets are excluded from Git.

---

## How It Works

### 1. Extraction and API Resilience

`src/entsoe_api.py`:

- reads the API token from the environment;
- calculates the correct UTC interval for a Romanian calendar day;
- requests Romanian day-ahead prices;
- parses the ENTSO-E XML response;
- supports `PT15M` and `PT60M` resolutions;
- filters observations to the requested Romanian date.

Temporary failures are retried for HTTP `429`, `500`, `502`, `503` and `504`, with up to five attempts and exponential backoff:

```text
2s → 4s → 8s → 16s
```

If ENTSO-E provides a numeric `Retry-After` header, it is respected. Requests also use a timeout.

Application logs record status, attempts and request duration using key-value messages.

### 2. dlt Ingestion

`src/dlt_pipeline.py` loads the parsed records into:

```text
raw.raw_entsoe_prices
```

The dlt resource uses:

```text
write_disposition = merge
primary_key = timestamp
```

This makes the load idempotent: rerunning the same date does not create duplicate timestamp records, while historical dates remain stored.

The ingestion layer also logs basic metrics such as `rows` and `duration_seconds`.

### 3. dbt Transformation and Testing

The analytical flow is:

```text
raw.raw_entsoe_prices
        ↓
main.stg_entsoe_prices
        ↓
main.daily_prices
```

`stg_entsoe_prices` standardizes the raw observations and derives the Romanian `price_date`.

`daily_prices` aggregates observations by date and calculates:

- average price;
- minimum price;
- maximum price;
- observation count.

### 4. Reporting and Orchestration

`src/report.py` reads `main.daily_prices` and prints the daily summary.

`run_pipeline.py` executes:

```text
1. ENTSO-E ingestion
2. dbt build
3. Daily price report
```

The workflow is fail-fast: if ingestion or `dbt build` fails, the following steps are not executed.

---

## Data Quality

dbt schema and custom SQL tests check that:

- required fields are not null;
- timestamps are unique;
- duplicate timestamps are rejected;
- electricity prices remain within the configured sanity range.

A validated build completes with:

```text
PASS=7
WARN=0
ERROR=0
SKIP=0
```

For a normal 24-hour Romanian day at 15-minute resolution, the ingestion layer expects 96 observations and logs a warning when the count differs.

---

## Example Output

```text
DATE                 AVG PRICE      MIN PRICE      MAX PRICE   OBSERVATIONS
2026-08-18              164.28         114.80         220.16             96
2026-08-19              167.65         123.35         224.07             96
2026-08-20              161.42          95.00         216.22             96
2026-08-21              169.56          55.98         229.78             96
2026-08-26              185.27         116.41         261.57             96
2026-09-02              197.88         100.64         336.59             96
```

Historical dates remain available because DuckDB persists between runs and dlt uses merge loading.

---

## Running the Pipeline

From the `entsoe_energy` directory:

```powershell
python run_pipeline.py
```

Without an argument, the pipeline processes yesterday according to `Europe/Bucharest`.

For a specific Romanian calendar date:

```powershell
python run_pipeline.py 2026-08-26
```

From the portfolio root:

```powershell
python entsoe_energy\run_pipeline.py 2026-08-26
```

A successful run ends with:

```text
PIPELINE COMPLETED SUCCESSFULLY
```

---

## Security

The ENTSO-E API token is stored locally in `.env`:

```text
ENTSOE_API_TOKEN=your_api_token_here
```

Secrets and generated artifacts such as `.env`, DuckDB files, local data, logs and dbt build output are excluded from version control.

---

## Production Improvements

The project is intentionally lightweight and runs locally. In a production environment, the next improvements would be:

- a scheduler/orchestrator such as Airflow, Dagster or Prefect for automated runs and backfills;
- CI/CD to run tests and `dbt build` automatically;
- unit tests for XML parsing and API edge cases;
- dedicated tests for daylight-saving-time transition days;
- centralized metrics and monitoring for freshness, latency and failures;
- alerting when data is missing, dbt tests fail or the API remains unavailable;
- a cloud warehouse or server database if data volume or the number of consumers grows.

---

## Key Engineering Concepts

`API integration` · `XML parsing` · `timezone handling` · `retry/backoff` · `idempotent ingestion` · `data modeling` · `data quality` · `application logging` · `fail-fast orchestration`