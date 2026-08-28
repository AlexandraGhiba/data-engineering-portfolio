import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON = Path(sys.executable)
DBT = PYTHON.parent / "Scripts" / "dbt.exe"


def run_command(command):
    """Run a command and stop if it fails."""

    result = subprocess.run(command, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        raise SystemExit(
            f"\nCommand failed: {' '.join(str(item) for item in command)}"
        )


def main():
    print("=" * 60)
    print("ENTSO-E ENERGY DATA PIPELINE")
    print("=" * 60)

    print("\n1. RUNNING ENTSO-E INGESTION")
    print("-" * 60)

    ingestion_command = [
        PYTHON,
        "src/dlt_pipeline.py",
    ]

    if len(sys.argv) > 1:
        ingestion_command.append(sys.argv[1])

    run_command(ingestion_command)

    print("\n2. RUNNING DBT BUILD")
    print("-" * 60)

    if not DBT.exists():
        raise FileNotFoundError(
            f"dbt executable not found: {DBT}"
        )

    run_command([
        DBT,
        "build",
    ])

    print("\n3. GENERATING DAILY PRICE REPORT")
    print("-" * 60)

    run_command([
        PYTHON,
        "src/report.py",
    ])

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()