from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


with DAG(
    dag_id="kaggle_sales_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1),
    },
    tags=["kaggle", "sales", "dbt"],
) as dag:

    load_raw_data = BashOperator(
        task_id="load_raw_data",
        bash_command="python scripts/load_raw_data.py",
        cwd="/opt/airflow/kaggle-star-schema",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="dbt run --profiles-dir .",
        cwd="/opt/airflow/kaggle-star-schema",
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="dbt test --profiles-dir .",
        cwd="/opt/airflow/kaggle-star-schema",
    )

    validate_warehouse = BashOperator(
        task_id="validate_warehouse",
        bash_command="""
        python -c "
import duckdb

con = duckdb.connect('dev.duckdb')

row_count = con.execute(
    'SELECT COUNT(*) FROM fact_orders'
).fetchone()[0]

print(f'fact_orders rows: {row_count}')

if row_count == 0:
    raise ValueError('fact_orders is empty')

con.close()
"
        """,
        cwd="/opt/airflow/kaggle-star-schema",
    )

    load_raw_data >> dbt_run >> dbt_test >> validate_warehouse