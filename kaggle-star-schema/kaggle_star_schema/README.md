# Kaggle Star Schema – dbt & DuckDB

An end-to-end analytics engineering project that transforms a Kaggle retail sales dataset into a dimensional **Star Schema** using **dbt** and **DuckDB**.

The project is designed to be reproducible: a new user can clone the repository and rebuild the complete warehouse from the source data with a single pipeline command.

## Architecture

```text
Excel Source Dataset
        |
        v
Python Raw Loader
        |
        v
DuckDB Raw Tables
 raw_orders
 raw_calendar
        |
        v
dbt Sources
        |
        v
Staging Models
 stg_orders
 stg_calendar
        |
        v
Star Schema
        |
        +-- dim_customer
        +-- dim_date
        +-- dim_location
        +-- dim_product
        |
        +-- fact_orders
        |
        v
dbt Tests + Documentation
```

## Data Pipeline

The complete pipeline is executed with:

```bash
python run_pipeline.py
```

It automatically:

1. Reads the source Excel workbook.
2. Creates `raw_orders` and `raw_calendar` in DuckDB.
3. Runs all dbt transformations.
4. Runs dbt data quality tests.
5. Generates dbt documentation.
6. Validates the final warehouse.

No pre-existing DuckDB database is required.

## Data Modeling

The final warehouse follows a Star Schema with one fact table and four dimensions.

### Fact Table

`fact_orders`

**Grain:** one row per source order line.

The fact table contains measures such as:

- `sales`
- `quantity`
- `discount`
- `profit`

It also contains surrogate foreign keys connecting each order line to the dimensions.

### Dimensions

- `dim_customer`
- `dim_date`
- `dim_location`
- `dim_product`

The final fact table contains **9,994 rows**.

## dbt Sources and Lineage

The raw DuckDB tables are declared as dbt sources in:

```text
models/staging/sources.yml
```

The staging models use:

```sql
{{ source('raw', 'orders') }}
{{ source('raw', 'calendar') }}
```

instead of querying the physical raw tables directly.

This makes the dependency from raw data to staging models visible in dbt Docs lineage.

## Data Quality

The project currently contains **21 dbt tests** covering key constraints such as:

- `not_null`
- `unique`

Current result:

```text
PASS=21
WARN=0
ERROR=0
```

If dbt model execution or testing fails, the pipeline stops with an error.

## Project Structure

```text
kaggle_star_schema/
│
├── data/
│   └── Retail-Supply-Chain-Sales-Dataset.xlsx
│
├── scripts/
│   └── load_raw_data.py
│
├── models/
│   ├── staging/
│   │   ├── sources.yml
│   │   ├── stg_orders.sql
│   │   └── stg_calendar.sql
│   │
│   ├── dimensions/
│   │   ├── dim_customer.sql
│   │   ├── dim_date.sql
│   │   ├── dim_location.sql
│   │   └── dim_product.sql
│   │
│   └── facts/
│       └── fact_orders.sql
│
├── profiles.yml
├── dbt_project.yml
├── requirements.txt
├── run_pipeline.py
└── README.md
```

## How to Run

### 1. Clone the repository

```bash
git clone <repository-url>
cd kaggle_star_schema
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the complete pipeline

```bash
python run_pipeline.py
```

A successful execution ends with:

```text
PIPELINE SUCCESS
```

## dbt Documentation

dbt documentation is generated automatically by the pipeline.

To explore the documentation and lineage locally:

```bash
dbt docs serve --profiles-dir .
```

## Results

A successful clean run produces:

- **9,994 fact rows**
- **5,009 distinct orders**
- **1,894 products**
- **793 customers**
- **21 / 21 dbt tests passing**

## Technologies

- **Python** – raw data loading and pipeline orchestration
- **dbt** – transformations, testing, sources, lineage, and documentation
- **DuckDB** – local analytical warehouse
- **SQL** – dimensional modeling and transformations
- **pandas / openpyxl** – Excel ingestion

## Key Takeaways

This project demonstrates a complete local analytics engineering workflow:

```text
Source Data
    ↓
Raw Ingestion
    ↓
DuckDB
    ↓
dbt Sources
    ↓
Staging
    ↓
Star Schema
    ↓
Data Quality Tests
    ↓
Documentation
```

The main focus is **reproducibility**: the DuckDB warehouse can be deleted completely and rebuilt from the source dataset by running a single command:

```bash
python run_pipeline.py
```