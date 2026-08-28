from pathlib import Path
import duckdb


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "raw"
DB_PATH = PROJECT_ROOT / "warehouse.duckdb"


def load_raw_trips() -> None:
    parquet_glob = str(
        RAW_DIR / "year=*" / "month=*" / "*.parquet"
    ).replace("\\", "/")

    print(f"DuckDB: {DB_PATH}")
    print(f"Reading Parquet files from: {parquet_glob}")

    conn = duckdb.connect(str(DB_PATH))

    conn.execute(
        f"""
        create or replace view raw_trips as
        select *
        from read_parquet(
            '{parquet_glob}',
            hive_partitioning = true
        )
        """
    )

    row_count = conn.execute(
        "select count(*) from raw_trips"
    ).fetchone()[0]

    print(f"raw_trips rows: {row_count:,}")

    columns = conn.execute(
        "describe raw_trips"
    ).fetchall()

    print("\nColumns:")
    for column in columns:
        print(f"- {column[0]} ({column[1]})")

    conn.close()


if __name__ == "__main__":
    load_raw_trips()