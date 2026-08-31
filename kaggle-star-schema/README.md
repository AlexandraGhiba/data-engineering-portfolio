# Kaggle Star Schema – dbt & DuckDB

End-to-end analytics engineering project that transforms a retail sales dataset into a dimensional **Star Schema** using **dbt, DuckDB, SQL, and Python**.

The entire warehouse can be rebuilt from the source Excel file with one command:

```bash
python run_pipeline.py
```

## Architecture

```text
Excel Dataset
      ↓
Python Loader
      ↓
DuckDB Raw Tables
      ↓
dbt Staging
      ↓
Star Schema
      ↓
Data Quality Tests
      ↓
dbt Documentation
```

## Star Schema

`fact_orders` is the central fact table, connected to four dimensions:

- `dim_date`
- `dim_customer`
- `dim_location`
- `dim_product`

![Star Schema](docs/star_schema.png)

**Fact table grain:** one row per source order line.

The fact table contains the main measures:

`sales` · `quantity` · `discount` · `profit`

and surrogate foreign keys to each dimension.

## Data Quality

The project includes **32 dbt tests** covering:

- `not_null` constraints
- uniqueness of keys
- referential integrity between fact and dimension tables
- uniqueness of the `fact_orders` grain
- validation of the `dim_product` grain

```text
PASS=32
WARN=0
ERROR=0
```

## dbt Lineage

dbt manages the transformation dependencies using `source()` and `ref()`:

```text
raw_orders ──→ stg_orders ──→ dimensions ──→ fact_orders
                                    ↑
raw_calendar → stg_calendar → dim_date
```

Interactive model lineage and documentation can be generated locally:

```bash
dbt docs generate
dbt docs serve --host 127.0.0.1 --port 8001
```

Then open `http://127.0.0.1:8001`.

## Project Structure

```text
kaggle_star_schema/
│
├── data/
├── scripts/
│   └── load_raw_data.py
│
├── models/
│   ├── staging/
│   ├── dimensions/
│   └── facts/
│
├── tests/
│   └── assert_dim_product_grain.sql
│
├── run_pipeline.py
├── dbt_project.yml
├── profiles.yml
├── requirements.txt
└── README.md
```

## Run the Project

```bash
git clone <repository-url>
cd kaggle-star-schema/kaggle_star_schema

python -m venv .venv
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python run_pipeline.py
```

A successful run builds the complete DuckDB warehouse, executes all dbt models and tests, and generates the documentation.

## Results

| Metric | Result |
|---|---:|
| Fact rows | **9,994** |
| Distinct orders | **5,009** |
| Products | **1,894** |
| Customers | **793** |
| dbt models | **7** |
| dbt tests | **32 / 32 passing** |

## Tech Stack

**Python** · **SQL** · **dbt** · **DuckDB** · **pandas** · **openpyxl**

## What This Project Demonstrates

- Dimensional modeling and Star Schema design
- Fact and dimension tables
- Surrogate keys and referential integrity
- dbt staging and model dependencies
- Automated data quality testing
- dbt documentation and lineage
- Reproducible Python pipeline orchestration