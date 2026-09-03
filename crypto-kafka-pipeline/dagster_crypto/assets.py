from pathlib import Path
import subprocess

import duckdb
from dagster import asset, MaterializeResult

import gspread
from google.oauth2.service_account import Credentials


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "crypto.duckdb"
DBT_PROJECT = PROJECT_ROOT / "dbt_crypto"

VENV_DBT = PROJECT_ROOT / ".venv" / "Scripts" / "dbt.exe"


@asset
def crypto_dbt_models() -> MaterializeResult:
    """Run dbt models and report row counts."""

    result = subprocess.run(
        [
            str(VENV_DBT),
            "run",
            "--project-dir",
            str(DBT_PROJECT),
            "--profiles-dir",
            str(DBT_PROJECT),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"dbt failed:\n{result.stdout}\n{result.stderr}"
        )

    with duckdb.connect(str(DB_PATH), read_only=True) as conn:
        raw_count = conn.execute(
            "SELECT COUNT(*) FROM raw_crypto_trades"
        ).fetchone()[0]

        staging_count = conn.execute(
            "SELECT COUNT(*) FROM stg_crypto_trades"
        ).fetchone()[0]

        mart_count = conn.execute(
            "SELECT COUNT(*) FROM mart_crypto_metrics"
        ).fetchone()[0]

    return MaterializeResult(
        metadata={
            "raw_trades": raw_count,
            "staging_trades": staging_count,
            "mart_rows": mart_count,
        }
    )


@asset(deps=[crypto_dbt_models])
def crypto_dbt_tests() -> MaterializeResult:
    """Run dbt data-quality tests."""

    result = subprocess.run(
        [
            str(VENV_DBT),
            "test",
            "--project-dir",
            str(DBT_PROJECT),
            "--profiles-dir",
            str(DBT_PROJECT),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"dbt tests failed:\n{result.stdout}\n{result.stderr}"
        )

    return MaterializeResult(
        metadata={
            "status": "PASS",
            "tests": 7,
        }
    )


@asset(deps=[crypto_dbt_tests])
def crypto_anomaly_check() -> MaterializeResult:
    """Compare the latest 10-minute volume against historical 10-minute windows."""

    with duckdb.connect(str(DB_PATH)) as conn:

        stats = conn.execute(
            """
            WITH windows AS (
                SELECT
                    DATE_TRUNC('minute', timestamp)
                    - INTERVAL '1 minute'
                    * (EXTRACT(MINUTE FROM timestamp)::INTEGER % 10)
                    AS window_start,
                    SUM(quantity) AS volume
                FROM raw_crypto_trades
                GROUP BY 1
            ),
            latest AS (
                SELECT MAX(window_start) AS latest_window
                FROM windows
            )
            SELECT
                w.window_start,
                w.volume
            FROM windows w
            CROSS JOIN latest l
            ORDER BY w.window_start DESC
            """
        ).fetchall()

        if not stats:
            return MaterializeResult(
                metadata={"status": "NO_DATA"}
            )

        latest_window = stats[0][0]
        recent_volume = float(stats[0][1] or 0)

        historical_volumes = [
            float(row[1] or 0)
            for row in stats[1:11]
        ]

        if historical_volumes:
            baseline_volume = sum(historical_volumes) / len(
                historical_volumes
            )
        else:
            baseline_volume = 0

        ratio = (
            recent_volume / baseline_volume
            if baseline_volume > 0
            else 0
        )

        is_anomaly = ratio >= 3
        status = "ANOMALY" if is_anomaly else "OK"

        trade_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM raw_crypto_trades
            WHERE timestamp >= ?
              AND timestamp < ?
            """,
            [
                latest_window,
                latest_window
                + __import__("datetime").timedelta(minutes=10),
            ],
        ).fetchone()[0]

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS crypto_anomalies (
                checked_at TIMESTAMP,
                window_start TIMESTAMP,
                recent_volume DOUBLE,
                baseline_volume DOUBLE,
                volume_ratio DOUBLE,
                trade_count BIGINT,
                status VARCHAR
            )
            """
        )

        conn.execute(
            """
            INSERT INTO crypto_anomalies
            VALUES (
                CURRENT_TIMESTAMP,
                ?,
                ?,
                ?,
                ?,
                ?,
                ?
            )
            """,
            [
                latest_window,
                recent_volume,
                baseline_volume,
                ratio,
                trade_count,
                status,
            ],
        )

    print(
        f"[ANOMALY CHECK] status={status} "
        f"recent_volume={recent_volume:.6f} "
        f"baseline={baseline_volume:.6f} "
        f"ratio={ratio:.2f}x"
    )

    return MaterializeResult(
        metadata={
            "status": status,
            "window_start": str(latest_window),
            "recent_volume": recent_volume,
            "baseline_volume": baseline_volume,
            "volume_ratio": ratio,
            "trade_count": trade_count,
        }
    )


# ============ CONFIG Google Sheets ============
SERVICE_ACCOUNT_FILE = str(
    PROJECT_ROOT / "service_account.json"
)

SPREADSHEET_ID = "1I4gAYeLyaVwmONhM7h373MGxzNYYt3ifL-UpgFjH4_8"

WORKSHEET_NAME = "LiveData"

SHEETS_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
# ================================================


@asset(deps=[crypto_anomaly_check])
def crypto_metrics_to_sheets() -> MaterializeResult:
    """Uploads mart_crypto_metrics into Google Sheets after the full pipeline runs."""

    with duckdb.connect(str(DB_PATH), read_only=True) as conn:
        df = conn.execute(
            "SELECT * FROM mart_crypto_metrics"
        ).fetchdf()

    for col in df.columns:
        if df[col].dtype.name.startswith("datetime"):
            df[col] = df[col].astype(str)

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SHEETS_SCOPES,
    )

    client = gspread.authorize(creds)
    sheet = client.open_by_key(SPREADSHEET_ID)

    try:
        worksheet = sheet.worksheet(WORKSHEET_NAME)

    except gspread.exceptions.WorksheetNotFound:
        worksheet = sheet.add_worksheet(
            title=WORKSHEET_NAME,
            rows=str(len(df) + 10),
            cols=str(len(df.columns) + 2),
        )

    worksheet.clear()

    values = [df.columns.tolist()] + df.values.tolist()

    worksheet.update(
        values,
        value_input_option="USER_ENTERED",
    )

    return MaterializeResult(
        metadata={
            "rows_uploaded": len(df),
            "worksheet": WORKSHEET_NAME,
        }
    )