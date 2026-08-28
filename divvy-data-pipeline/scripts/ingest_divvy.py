from pathlib import Path
from io import BytesIO
import zipfile
import requests
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "raw"


def ingest_month(year: int, month: int) -> None:
    ym = f"{year}{month:02d}"
    url = f"https://divvy-tripdata.s3.amazonaws.com/{ym}-divvy-tripdata.zip"

    output_dir = RAW_DIR / f"year={year}" / f"month={month:02d}"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"divvy_trips_{ym}.parquet"

    print(f"Downloading: {url}")

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with zipfile.ZipFile(BytesIO(response.content)) as zip_file:
        csv_files = [
            name for name in zip_file.namelist()
            if name.lower().endswith(".csv")
        ]

        if not csv_files:
            raise ValueError("No CSV file found inside ZIP archive.")

        csv_name = csv_files[0]
        print(f"Reading: {csv_name}")

        with zip_file.open(csv_name) as csv_file:
            df = pd.read_csv(csv_file)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    df.to_parquet(output_file, index=False)

    print(f"Saved Parquet: {output_file}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Ingest one month of Divvy trip data."
    )

    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year to ingest, e.g. 2024",
    )

    parser.add_argument(
        "--month",
        type=int,
        required=True,
        choices=range(1, 13),
        help="Month to ingest, from 1 to 12",
    )

    args = parser.parse_args()

    ingest_month(args.year, args.month)