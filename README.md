      Data Engineering Portfolio

      A portfolio of end-to-end batch and streaming data engineering
      projects built with Python, SQL and modern open-source tools.

      The projects demonstrate API ingestion, event streaming, orchestration,
      analytical storage, dbt transformations, dimensional modeling, SCD Type
      2, data quality testing and reporting.

      Stack

      Area              Technologies

      Programming       Python · SQL
      Transformation    dbt
      Storage           DuckDB · Parquet
      Ingestion         dlt · REST APIs · WebSockets
      Orchestration     Apache Airflow · Dagster
      Streaming         Apache Kafka
      Modeling          Star Schema · SCD Type 2 · Incremental Models
      Infrastructure    Docker
      Reporting         Google Sheets · Looker Studio
      Version Control   Git · GitHub

      Projects

      1. 🌦️ Weather Data Pipeline

      Batch pipeline that retrieves hourly weather data from the Open-Meteo
      API for five Romanian cities and transforms it into daily analytical
      models.

      Open-Meteo API → Python → dlt → DuckDB → dbt → Data Quality Tests

      Demonstrates: REST API ingestion, normalization, analytical storage,
      SQL transformations and automated validation.

      Stack: Python · dlt · DuckDB · dbt · SQL

      2. ⚡ ENTSO-E Energy Price Pipeline

      Batch pipeline that extracts day-ahead electricity prices from the
      ENTSO-E Transparency Platform, parses XML responses and produces
      daily analytical outputs.

      ENTSO-E API → Python → XML Parsing → dlt → DuckDB → dbt → Daily Report

      Demonstrates: authenticated API ingestion, XML parsing, dbt
      transformations and data quality testing.

      Stack: Python · ENTSO-E API · dlt · DuckDB · dbt · SQL

      3. 🛒 Kaggle Superstore --- Star Schema

      Dimensional modeling project that transforms the Kaggle Superstore
      dataset into an analytical Star Schema.

      Kaggle Dataset → Staging → Dimensions + Fact → dbt Tests → Business Validation

      The final model includes fact_orders, dim_date, dim_customer,
      dim_location and dim_product.

      9,994 fact rows · 21 dbt data quality tests

      Demonstrates: dimensional modeling, surrogate keys, fact/dimension
      design and business validation.

      Stack: Python · dbt · DuckDB · SQL

      4. ₿ Crypto Kafka Pipeline --- Real-Time Streaming

      Real-time pipeline that captures BTCUSDT trades from the Binance
      WebSocket API and processes them through Kafka, DuckDB and dbt.

      Binance WebSocket
            ↓
      Kafka Producer
            ↓
      Kafka Topic
            ↓
      Kafka Consumer
            ↓
      DuckDB → dbt → Anomaly Detection
            ↓
      Google Sheets → Looker Studio

      Dagster orchestrates transformations, tests, anomaly detection and
      reporting.

      Demonstrates: real-time streaming, producer/consumer architecture,
      orchestration and anomaly detection.

      Stack: Python · Kafka · Binance WebSocket · DuckDB · dbt · Dagster ·
      Docker

      5. 🚲 Divvy Bike-Share Data Pipeline

      Monthly batch pipeline that processes historical Divvy bike-share
      trips using Apache Airflow, Parquet, DuckDB and dbt.

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
      Analytical Marts + dbt Tests

      The project processes 669,724 raw trips from January--March 2024
      into 669,493 unique analytical fact rows.

      Key features include:

      parameterized monthly Airflow orchestration

      Parquet partitioning by year and month

      incremental fct_trips keyed by ride_id

      SCD Type 2 station history

      time-aware station foreign keys

      station imbalance and monthly usage marts

      station rename/relocation and potential re-issued ID analysis

      automated dbt data quality tests

      Final dbt validation: 12 PASS · 1 WARN · 0 ERROR

      Demonstrates: Airflow orchestration, incremental processing, SCD
      Type 2, temporal modeling, idempotency and data quality.

      Stack: Python · Apache Airflow · Parquet · DuckDB · dbt · SQL ·
      Docker

      Project Structure

      data-engineering-portfolio/
      │
      ├── weather/
      ├── entsoe_energy/
      ├── kaggle-star-schema/
      ├── crypto-kafka-pipeline/
      ├── divvy-data-pipeline/
      │
      └── README.md

      Each project contains its own README with architecture, implementation
      details and run instructions.

      Key Capabilities

      Across the five projects, the portfolio demonstrates:

      batch and real-time data pipelines

      REST API, WebSocket and XML ingestion

      Apache Kafka producer/consumer architecture

      Apache Airflow and Dagster orchestration

      DuckDB analytical storage

      partitioned Parquet datasets

      dbt staging, intermediate and mart models

      Star Schema and dimensional modeling

      SCD Type 2 historical modeling

      incremental and idempotent processing

      automated data quality testing

      anomaly detection and analytical reporting

      Docker-based reproducible environments

      How to Run

      Clone the portfolio:

      git clone https://github.com/AlexandraGhiba/data-engineering-portfolio.git
      cd data-engineering-portfolio

      The projects are intentionally independent. Open the README inside the
      project you want to run and follow its project-specific instructions.

      The Divvy and Crypto Kafka projects use Docker-based
      infrastructure. The other projects can be run independently without
      starting Kafka or Airflow.

      Reproducibility

      Each project follows the same general engineering pattern:

      Extract → Ingest → Store → Transform → Test → Validate → Analyze

      The projects are designed to run locally using open-source data
      engineering technologies.

      Author

      Ghiba Alexandra

      Data Engineering portfolio focused on practical experience building
      reliable pipelines from ingestion and storage through transformation,
      orchestration, validation and analytics.