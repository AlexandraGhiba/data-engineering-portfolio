from datetime import timedelta
from pathlib import Path
import subprocess

import pendulum

from airflow import DAG
from airflow.models.param import Param
from airflow.operators.python import PythonOperator


PROJECT_ROOT = Path("/opt/airflow")
SCRIPTS_DIR = PROJECT_ROOT / "scripts"
DBT_PROJECT_DIR = PROJECT_ROOT / "dbt_project"
PROFILES_DIR = PROJECT_ROOT


DEFAULT_ARGS = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}


def run_command(command: list[str]) -> None:
    print("Running:", " ".join(command))

    subprocess.run(
        command,
        cwd=PROJECT_ROOT,
        check=True,
        text=True,
    )


def get_processing_period(context):
    year = int(context["params"]["year"])
    month = int(context["params"]["month"])
    return year, month


def ingest_month(**context) -> None:
    year, month = get_processing_period(context)

    run_command(
        [
            "python",
            str(SCRIPTS_DIR / "ingest_divvy.py"),
            "--year",
            str(year),
            "--month",
            str(month),
        ]
    )


def load_duckdb() -> None:
    run_command(
        [
            "python",
            str(SCRIPTS_DIR / "load_duckdb.py"),
        ]
    )


def build_staging_and_intermediate() -> None:
    run_command(
        [
            "dbt",
            "run",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(PROFILES_DIR),
            "--select",
            "stg_trips",
            "int_trips_enriched",
            "int_station_observations",
        ]
    )


def build_station_current(**context) -> None:
    year, month = get_processing_period(context)

    run_command(
        [
            "dbt",
            "run",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(PROFILES_DIR),
            "--select",
            "int_station_current",
            "--vars",
            f"{{processing_year: {year}, processing_month: {month}}}",
        ]
    )


def run_station_snapshot(**context) -> None:
    year, month = get_processing_period(context)

    run_command(
        [
            "dbt",
            "snapshot",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(PROFILES_DIR),
            "--vars",
            f"{{processing_year: {year}, processing_month: {month}}}",
        ]
    )


def build_fact_and_marts() -> None:
    run_command(
        [
            "dbt",
            "run",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(PROFILES_DIR),
            "--select",
            "dim_stations",
            "fct_trips",
            "mart_station_imbalance",
            "mart_monthly_usage",
            "mart_station_changes",
        ]
    )


def run_dbt_tests() -> None:
    run_command(
        [
            "dbt",
            "test",
            "--project-dir",
            str(DBT_PROJECT_DIR),
            "--profiles-dir",
            str(PROFILES_DIR),
        ]
    )


with DAG(
    dag_id="divvy_monthly_pipeline",
    description="Monthly Divvy ingestion and dbt transformation pipeline",
    default_args=DEFAULT_ARGS,
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    params={
        "year": Param(
            2024,
            type="integer",
            minimum=2013,
            maximum=2030,
            description="Year to process",
        ),
        "month": Param(
            1,
            type="integer",
            minimum=1,
            maximum=12,
            description="Month to process",
        ),
    },
    tags=["divvy", "dbt", "duckdb"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_month",
        python_callable=ingest_month,
    )

    load_task = PythonOperator(
        task_id="load_duckdb",
        python_callable=load_duckdb,
    )

    staging_task = PythonOperator(
        task_id="build_staging_and_intermediate",
        python_callable=build_staging_and_intermediate,
    )

    station_current_task = PythonOperator(
        task_id="build_station_current",
        python_callable=build_station_current,
    )

    snapshot_task = PythonOperator(
        task_id="run_station_snapshot",
        python_callable=run_station_snapshot,
    )

    marts_task = PythonOperator(
        task_id="build_fact_and_marts",
        python_callable=build_fact_and_marts,
    )

    tests_task = PythonOperator(
        task_id="run_dbt_tests",
        python_callable=run_dbt_tests,
    )

    (
        ingest_task
        >> load_task
        >> staging_task
        >> station_current_task
        >> snapshot_task
        >> marts_task
        >> tests_task
    )