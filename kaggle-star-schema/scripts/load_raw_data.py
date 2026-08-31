from pathlib import Path

import duckdb
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXCEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "Retail-Supply-Chain-Sales-Dataset.xlsx"
)

DUCKDB_PATH = PROJECT_ROOT / "dev.duckdb"


def main():
    if not EXCEL_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {EXCEL_PATH}"
        )

    print(f"Loading source data from: {EXCEL_PATH}")
    print(f"DuckDB database: {DUCKDB_PATH}")

    orders = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Retails Order Full Dataset",
    )

    calendar = pd.read_excel(
        EXCEL_PATH,
        sheet_name="Calendar Table",
    )

    con = duckdb.connect(str(DUCKDB_PATH))

    try:
        con.register("orders_df", orders)
        con.register("calendar_df", calendar)

        con.execute("""
            CREATE OR REPLACE TABLE raw_orders AS
            SELECT *
            FROM orders_df
        """)

        con.execute("""
            CREATE OR REPLACE TABLE raw_calendar AS
            SELECT *
            FROM calendar_df
        """)

    finally:
        con.close()

    print("Raw data loaded successfully.")
    print(f"Orders: {len(orders):,} rows")
    print(f"Calendar: {len(calendar):,} rows")


if __name__ == "__main__":
    main()