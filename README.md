# 🚀 Data Engineering Portfolio

A portfolio of **end-to-end data engineering projects** covering batch processing, real-time streaming, orchestration, dimensional modeling, data quality, and analytics.

Built with **Python, SQL, dbt, DuckDB, Apache Airflow, Apache Kafka, Dagster, Docker, and Parquet**.

---

## 🛠️ Tech Stack

| Area | Technologies |
|---|---|
| **Programming** | Python · SQL |
| **Transformation** | dbt |
| **Storage** | DuckDB · Parquet |
| **Ingestion** | dlt · REST APIs · WebSockets · XML |
| **Orchestration** | Apache Airflow · Dagster |
| **Streaming** | Apache Kafka |
| **Data Modeling** | Star Schema · SCD Type 2 · Incremental Models |
| **Infrastructure** | Docker |
| **Reporting** | Google Sheets · Looker Studio |
| **Version Control** | Git · GitHub |

---

# 📂 Projects

## 1. 🌦️ Weather Data Pipeline

A batch data pipeline that retrieves hourly weather data from the **Open-Meteo API** for five Romanian cities and transforms it into daily analytical models.

```text
Open-Meteo API
      ↓
Python + dlt
      ↓
DuckDB
      ↓
dbt Transformations
      ↓
Data Quality Tests
```

**Key concepts:** REST API ingestion · normalization · analytical storage · SQL transformations · automated testing

**Stack:** `Python` `dlt` `DuckDB` `dbt` `SQL`

📁 [`dbt_weather/`](./dbt_weather/)

---

## 2. ⚡ ENTSO-E Energy Price Pipeline

A batch pipeline that extracts Romanian day-ahead electricity prices from the **ENTSO-E Transparency Platform**, handles XML responses and timezone-aware data, and produces validated daily analytics.

```text
ENTSO-E API
      ↓
Python + XML Parsing
      ↓
dlt
      ↓
DuckDB
      ↓
dbt
      ↓
Daily Price Report
```

**Key concepts:** authenticated API ingestion · XML parsing · timezone handling · transformations · data quality

**Stack:** `Python` `dlt` `DuckDB` `dbt` `SQL`

📁 [`entsoe_energy/`](./entsoe_energy/)

---

## 3. 🛒 Kaggle Retail Star Schema

An end-to-end analytics engineering project that transforms a retail dataset into a dimensional **Star Schema** using Python, DuckDB, dbt, Apache Airflow, and Docker.

```text
Excel Dataset
      ↓
Python Raw Loader
      ↓
DuckDB Raw Tables
      ↓
dbt Staging
      ↓
Dimensions + Fact
      ↓
dbt Tests
      ↓
Warehouse Validation

Orchestrated with Apache Airflow
running in Docker
```

### Airflow DAG

```text
load_raw_data
      ↓
dbt_run
      ↓
dbt_test
      ↓
validate_warehouse
```

### Data Model

```text
             dim_customer
                  │
dim_date ─── fact_orders ─── dim_product
                  │
             dim_location
```

**Fact grain:** one row per source order line.

**Results:**

- **9,994** fact rows
- **5,009** distinct orders
- **1,894** products
- **793** customers
- **32 / 32 dbt tests passing**

**Key concepts:** Star Schema · dimensional modeling · surrogate keys · fact/dimension design · Apache Airflow orchestration · Docker · automated data quality · warehouse validation

**Stack:** `Python` `Apache Airflow` `Docker` `dbt` `DuckDB` `SQL` `pandas`

📁 [`kaggle-star-schema/`](./kaggle-star-schema/)

---

## 4. ₿ Crypto Kafka Pipeline

A **real-time streaming pipeline** that captures live BTCUSDT trades from the Binance WebSocket API and processes them through Kafka, DuckDB, dbt, and Dagster.

```text
Binance WebSocket
      ↓
Kafka Producer
      ↓
Kafka Topic
      ↓
Kafka Consumer
      ↓
DuckDB
      ↓
dbt
      ↓
Anomaly Detection
      ↓
Google Sheets
      ↓
Looker Studio
```

Dagster orchestrates the analytical workflow, including dbt transformations, testing, anomaly detection, and reporting.

**Key concepts:** real-time streaming · producer/consumer architecture · orchestration · anomaly detection · automated reporting

**Stack:** `Python` `Kafka` `WebSockets` `DuckDB` `dbt` `Dagster` `Docker`

📁 [`crypto-kafka-pipeline/`](./crypto-kafka-pipeline/)

---

## 5. 🚲 Divvy Bike-Share Data Pipeline

A production-style monthly batch pipeline processing historical **Divvy bike-share trips** with Apache Airflow, Parquet, DuckDB, and dbt.

```text
Divvy ZIP / CSV
      ↓
Apache Airflow
      ↓
Python Ingestion
      ↓
Partitioned Parquet
      ↓
DuckDB
      ↓
dbt Staging + Intermediate
      ↓
SCD Type 2 Station History
      ↓
dim_stations + fct_trips
      ↓
Analytical Marts
      ↓
dbt Tests
```

### Results

| Metric | Result |
|---|---:|
| Raw trips processed | **669,724** |
| Analytical fact rows | **669,493** |
| Period | **Jan–Mar 2024** |
| dbt validation | **12 PASS · 1 WARN · 0 ERROR** |

### Engineering Features

- Parameterized monthly **Airflow orchestration**
- Parquet partitioning by `year` and `month`
- Incremental `fct_trips` keyed by `ride_id`
- **SCD Type 2** station history
- Time-aware station foreign keys
- Station imbalance and monthly usage marts
- Station rename / relocation analysis
- Automated dbt data-quality tests
- Idempotent monthly processing

**Key concepts:** orchestration · incremental processing · SCD Type 2 · temporal modeling · idempotency · data quality

**Stack:** `Python` `Apache Airflow` `Parquet` `DuckDB` `dbt` `SQL` `Docker`

📁 [`divvy-data-pipeline/`](./divvy-data-pipeline/)

---

# 🧠 What This Portfolio Demonstrates

Across the five projects:

- **Batch and real-time data pipelines**
- REST API, WebSocket and XML ingestion
- Apache Kafka producer / consumer architecture
- Apache Airflow and Dagster orchestration
- DuckDB analytical storage
- Partitioned Parquet datasets
- dbt staging, intermediate and mart layers
- Star Schema dimensional modeling
- SCD Type 2 historical modeling
- Incremental and idempotent processing
- Automated data-quality testing
- Anomaly detection
- Analytical reporting
- Docker-based reproducible environments

---

# 📁 Repository Structure

```text
data-engineering-portfolio/
│
├── crypto-kafka-pipeline/
├── dbt_weather/
├── divvy-data-pipeline/
├── entsoe_energy/
├── kaggle-star-schema/
│
├── .gitignore
└── README.md
```

Each project contains its own **README** with architecture, implementation details, setup instructions, and execution steps.

---

# ▶️ Getting Started

Clone the complete portfolio:

```bash
git clone https://github.com/AlexandraGhiba/data-engineering-portfolio.git
cd data-engineering-portfolio
```

The projects are intentionally independent. Open the README inside the project you want to explore for project-specific setup and execution instructions.

> **Note:** The Divvy, Crypto Kafka, and Kaggle Star Schema projects use Docker-based infrastructure. The Kaggle and Divvy projects use Apache Airflow for orchestration, while the Crypto Kafka project uses Dagster for analytical workflow orchestration.

---

# 🔄 Engineering Approach

The projects follow a common data engineering lifecycle:

```text
Extract → Ingest → Store → Transform → Test → Validate → Analyze
```

The focus is on building **reproducible, testable, and maintainable data pipelines** using modern open-source data engineering tools.

---

# 👩‍💻 Author

**Ghiba Alexandra**

Data Engineering portfolio focused on practical experience building reliable pipelines from **ingestion and storage through transformation, orchestration, data quality, and analytics**.