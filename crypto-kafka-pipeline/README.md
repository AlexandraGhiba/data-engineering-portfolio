# 🚀 Crypto Kafka Pipeline

**Real-time data pipeline** that ingests live **BTCUSDT trades from Binance**, streams them through **Kafka**, transforms and tests the data with **dbt**, orchestrates the workflow with **Dagster**, and exports aggregated metrics to **Google Sheets / Looker Studio**.

## 🏗️ Architecture

```text
Binance WebSocket
      ↓
Kafka Producer
      ↓
Kafka topic: crypto-trades
      ↓
Kafka Consumer
      ↓
DuckDB: raw_crypto_trades
      ↓
dbt: stg_crypto_trades
      ↓
dbt: mart_crypto_metrics
      ↓
Dagster
   ├── dbt tests
   ├── anomaly detection
   └── Google Sheets export
      ↓
Looker Studio
```

## 🛠️ Tech Stack

- **Apache Kafka** — real-time event streaming
- **Binance WebSocket API** — live BTCUSDT trade data
- **DuckDB** — analytical database
- **dbt** — SQL transformations and data-quality testing
- **Dagster** — orchestration, scheduling, and asset lineage
- **Google Sheets** — metrics export
- **Looker Studio** — dashboard and visualization
- **Docker** — local Kafka environment

## 🔄 How It Works

### 1. Real-Time Ingestion

**`producer.py`** connects to the **Binance WebSocket API** and publishes every BTCUSDT trade to:

```text
Kafka topic: crypto-trades
```

Each event contains:

```text
timestamp | symbol | price | quantity | trade_id
```

**`consumer.py`** reads the Kafka messages and stores them in:

```text
DuckDB → raw_crypto_trades
```

The consumer uses:

```python
auto_offset_reset="latest"
```

so a new consumer group starts with **newly arriving Kafka messages** instead of replaying the entire retained history.

### 2. dbt Transformation

The raw DuckDB table is declared as a **dbt source**:

```sql
{{ source('crypto', 'raw_crypto_trades') }}
```

The transformation flow is:

```text
raw_crypto_trades
      ↓
stg_crypto_trades
      ↓
mart_crypto_metrics
```

**`stg_crypto_trades`** cleans, types, and validates raw trades.

**`mart_crypto_metrics`** aggregates trades into **1-minute buckets** and calculates:

- **trade count**
- **average price**
- **minimum / maximum price**
- **trading volume**
- **traded value**

### 3. Data Quality

The project contains **7 dbt data tests**:

- **5 `not_null` tests** — timestamp, symbol, price, quantity, trade_id
- **`price_positive`**
- **`quantity_positive`**

Run the complete dbt validation with:

```powershell
dbt build --project-dir dbt_crypto
```

Successful validation:

```text
PASS=9
WARN=0
ERROR=0
```

### 4. Dagster Orchestration

**Dagster** orchestrates the analytical pipeline:

```text
crypto_dbt_models
      ↓
crypto_dbt_tests
      ↓
crypto_anomaly_check
      ↓
crypto_metrics_to_sheets
```

The pipeline is scheduled to run **every 10 minutes**.

### 5. Anomaly Detection

The pipeline compares **recent trading volume** against a **historical baseline**.

A large volume spike is flagged as:

```text
ANOMALY
```

Otherwise:

```text
PASS
```

Results are stored in the **`crypto_anomalies`** table.

### 6. Reporting

The final **`mart_crypto_metrics`** dataset is exported to:

```text
Google Sheets → LiveData
```

with:

```text
minute_bucket
symbol
trade_count
avg_price
max_price
min_price
volume
traded_value
```

The exported data can then feed a **Looker Studio dashboard**.

---

## 📁 Project Structure

```text
crypto-kafka-pipeline/
│
├── producer.py              # Binance → Kafka
├── consumer.py              # Kafka → DuckDB
├── run_pipeline.py          # Runs streaming pipeline + dbt
│
├── dagster_crypto/
│   ├── assets.py            # Dagster assets
│   └── definitions.py       # Definitions + schedule
│
├── dbt_crypto/
│   ├── models/
│   │   ├── staging/         # stg_crypto_trades
│   │   └── marts/           # mart_crypto_metrics
│   └── tests/               # dbt custom tests
│
├── data/
│   └── crypto.duckdb        # Local DB (gitignored)
│
├── service_account.json     # Google credentials (gitignored)
└── README.md
```

## ⚙️ Setup

### 1. Create the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install kafka-python websockets duckdb dbt-duckdb dagster dagster-webserver gspread google-auth
```

### 2. Start Kafka

Kafka must be available at:

```text
localhost:9092
```

If using Docker:

```powershell
docker compose up -d
docker ps
```

Verify the connection:

```powershell
Test-NetConnection localhost -Port 9092
```

Expected:

```text
TcpTestSucceeded : True
```

### 3. Run the Streaming Pipeline

```powershell
python run_pipeline.py
```

You should see live messages from both components:

```text
[PRODUCER] BTCUSDT | ...
[CONSUMER] Saved | BTCUSDT | ...
```

Let the pipeline collect data for **a few minutes**.

Press **`CTRL+C`** to stop it.

The script then stops the producer and consumer and runs the **dbt transformations**.

### 4. Validate dbt

```powershell
dbt build --project-dir dbt_crypto
```

Expected:

```text
PASS=9 WARN=0 ERROR=0
```

### 5. Start Dagster

```powershell
dagster dev -m dagster_crypto.definitions
```

Open the Dagster UI:

**`http://127.0.0.1:3000`**

Materialize:

```text
crypto_dbt_models
      ↓
crypto_dbt_tests
      ↓
crypto_anomaly_check
      ↓
crypto_metrics_to_sheets
```

### 6. Verify Google Sheets

Open the **`LiveData`** worksheet.

You should see the latest aggregated BTCUSDT metrics produced by **`mart_crypto_metrics`**.

---

## 🔐 Google Sheets Configuration

Create a **Google Cloud service account** with access to:

- **Google Sheets API**
- **Google Drive API**

Save the credentials as:

```text
service_account.json
```

Share the target Google Sheet with the **service account email** and give it **Editor** access.

Configure:

```python
SPREADSHEET_ID = "..."
WORKSHEET_NAME = "LiveData"
```

inside **`dagster_crypto/assets.py`**.

> ⚠️ **Never commit `service_account.json`.** It must remain in `.gitignore`.

---

## 🎯 What This Project Demonstrates

- **Real-time data ingestion** with Kafka
- **Producer / consumer architecture**
- **Live WebSocket integration**
- **Analytical storage** with DuckDB
- **dbt sources and SQL transformations**
- **Automated data-quality testing**
- **Data orchestration and scheduling** with Dagster
- **Trading-volume anomaly detection**
- **Google Sheets integration**
- **Looker Studio reporting**
- **End-to-end data pipeline design**

## 🔮 Possible Improvements

- **dbt incremental models**
- Support for **multiple crypto symbols**
- **Slack / email alerts** for detected anomalies
- Move from DuckDB to a **cloud data warehouse**
- Deploy Dagster with **persistent storage**
- Add **monitoring and observability**