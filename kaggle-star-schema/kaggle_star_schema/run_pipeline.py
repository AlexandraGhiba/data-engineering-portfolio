import subprocess
import sys
from pathlib import Path

import duckdb


PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

DB_PATH = PROJECT_ROOT / "dev.duckdb"
RAW_LOADER = PROJECT_ROOT / "scripts" / "load_raw_data.py"
PROFILES_DIR = PROJECT_ROOT
DBT = "dbt"


def run_command(command, step_name):
    print("\n" + "=" * 60)
    print(step_name)
    print("=" * 60)

    result = subprocess.run(
        command,
        cwd=PROJECT_ROOT,
    )

    if result.returncode != 0:
        print(f"\nFAILED: {step_name}")
        sys.exit(result.returncode)

    print(f"\nSUCCESS: {step_name}")


def main():
    print("=" * 60)
    print("       KAGGLE STAR SCHEMA - PIPELINE")
    print("=" * 60)

    print(f"\nPython: {PYTHON}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Database: {DB_PATH}")

    run_command(
        [PYTHON, str(RAW_LOADER)],
        "[1/4] Loading raw source data",
    )

    run_command(
        [
            DBT,
            "run",
            "--profiles-dir",
            str(PROFILES_DIR),
        ],
        "[2/4] Running dbt models",
    )

    run_command(
        [
            DBT,
            "test",
            "--profiles-dir",
            str(PROFILES_DIR),
        ],
        "[3/4] Running dbt tests",
    )

    run_command(
        [
            DBT,
            "docs",
            "generate",
            "--profiles-dir",
            str(PROFILES_DIR),
        ],
        "[4/4] Generating dbt documentation",
    )

    print("\n" + "=" * 60)
    print("VALIDATING DATABASE")
    print("=" * 60)

    try:
        con = duckdb.connect(str(DB_PATH))

        fact_rows = con.sql(
            "SELECT COUNT(*) FROM fact_orders"
        ).fetchone()[0]

        models = con.sql("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'main'
            ORDER BY table_name
        """).fetchall()

        con.close()

        print(f"fact_orders rows: {fact_rows:,}")

        print("\nAvailable tables/views:")

        for model in models:
            print(f"  - {model[0]}")

    except Exception as exc:
        print(f"\nDatabase validation failed: {exc}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("              PIPELINE SUCCESS")
    print("=" * 60)
    print("Raw data load: SUCCESS")
    print("dbt models: SUCCESS")
    print("dbt tests: SUCCESS")
    print("dbt docs: SUCCESS")
    print(f"fact_orders: {fact_rows:,} rows")
    print("=" * 60)


if __name__ == "__main__":
    main()
