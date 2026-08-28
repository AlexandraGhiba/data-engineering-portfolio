import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

import dlt
import duckdb


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "weather_pipeline.duckdb"

API_URL = "https://api.open-meteo.com/v1/forecast"

DATASET = "weather_data"
TABLE = "weather_data"

CITIES = {
    "Bucharest": (44.4268, 26.1025),
    "Cluj-Napoca": (46.7712, 23.6236),
    "Iasi": (47.1585, 27.6014),
    "Timisoara": (45.7489, 21.2087),
    "Constanta": (44.1598, 28.6348),
}

HOURLY = ",".join([
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
    "precipitation",
    "cloud_cover",
])


# ============================================================
# 1. EXTRACT
# ============================================================

def fetch_weather(city, latitude, longitude):
    """Fetch 30 days of hourly weather data."""

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": HOURLY,
        "past_days": 30,
        "forecast_days": 0,
        "timezone": "Europe/Bucharest",
    }

    url = f"{API_URL}?{urlencode(params)}"

    with urlopen(url, timeout=30) as response:
        data = json.load(response)

    hourly = data["hourly"]

    return [
        {
            "city": city,
            "timestamp": timestamp,
            "temperature": hourly["temperature_2m"][i],
            "humidity": hourly["relative_humidity_2m"][i],
            "wind_speed": hourly["wind_speed_10m"][i],
            "precipitation": hourly["precipitation"][i],
            "cloud_cover": hourly["cloud_cover"][i],
        }
        for i, timestamp in enumerate(hourly["time"])
    ]


# ============================================================
# 2. LOAD WITH DLT
# ============================================================

@dlt.resource(
    name=TABLE,
    write_disposition="replace",
)
def weather_data():
    """Fetch weather data for all cities."""

    for city, (latitude, longitude) in CITIES.items():
        yield fetch_weather(city, latitude, longitude)


def load_data():
    """Load weather data into DuckDB."""

    pipeline = dlt.pipeline(
        pipeline_name="weather_pipeline",
        destination=dlt.destinations.duckdb(str(DB_PATH)),
        dataset_name=DATASET,
    )

    pipeline.run(weather_data())


# ============================================================
# 3. VALIDATE DUCKDB
# ============================================================

def validate():
    """Run basic SQL data quality checks."""

    table = f"{DATASET}.{TABLE}"

    with duckdb.connect(str(DB_PATH)) as conn:

        total_rows = conn.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]

        city_count = conn.execute(
            f"SELECT COUNT(DISTINCT city) FROM {table}"
        ).fetchone()[0]

        null_count = conn.execute(
            f"""
            SELECT COUNT(*)
            FROM {table}
            WHERE city IS NULL
               OR timestamp IS NULL
               OR temperature IS NULL
            """
        ).fetchone()[0]

    print(f"Rows: {total_rows:,}")
    print(f"Cities: {city_count}")
    print(f"Critical NULLs: {null_count}")

    assert total_rows > 0, "No data found in DuckDB."
    assert city_count == len(CITIES), (
        f"Expected {len(CITIES)} cities, found {city_count}."
    )
    assert null_count == 0, (
        f"Found {null_count} records with critical NULL values."
    )

    print("DuckDB validation passed.")


# ============================================================
# 4. DBT
# ============================================================

def run_dbt():
    """Run dbt build using dbt from the active environment."""
    dbt_executable = shutil.which("dbt")

    if dbt_executable is None:
        raise RuntimeError(
            "dbt was not found in the active Python environment. "
            "Install dependencies with: pip install -r requirements.txt"
        )

    subprocess.run(
        [
            dbt_executable,
            "build",
            "--profiles-dir",
            str(BASE_DIR),
        ],
        cwd=BASE_DIR,
        check=True,
    )

    print("dbt build passed.")


# ============================================================
# 5. MAIN PIPELINE
# ============================================================

def main():

    print("Starting weather pipeline...")

    # API → dlt → DuckDB
    load_data()

    # Validate raw data
    validate()

    # Transform + test
    run_dbt()

    print("Pipeline completed successfully!")


if __name__ == "__main__":
    main()