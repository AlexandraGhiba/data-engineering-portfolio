import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
DBT = ROOT / ".venv" / "Scripts" / "dbt.exe"
DBT_PROJECT = ROOT / "dbt_crypto"


def run_dbt():
    print("\n[PIPELINE] Running dbt...")

    result = subprocess.run(
        [
            str(DBT),
            "run",
            "--project-dir",
            str(DBT_PROJECT),
        ],
        cwd=DBT_PROJECT,
    )

    if result.returncode != 0:
        raise RuntimeError("dbt run failed")

    print("[PIPELINE] dbt completed successfully.")


def main():

    print("=" * 60)
    print("CRYPTO STREAMING PIPELINE")
    print("=" * 60)

    producer = subprocess.Popen(
        [str(VENV_PYTHON), str(ROOT / "producer.py")]
    )

    consumer = subprocess.Popen(
        [str(VENV_PYTHON), str(ROOT / "consumer.py")]
    )

    print("[PIPELINE] Producer started.")
    print("[PIPELINE] Consumer started.")

    try:

        print("[PIPELINE] Streaming... Press CTRL+C to stop.")

        while True:
            time.sleep(5)

    except KeyboardInterrupt:

        print("\n[PIPELINE] Stopping streaming services...")

        producer.terminate()
        consumer.terminate()

        producer.wait()
        consumer.wait()

        print("[PIPELINE] Streaming stopped.")

        run_dbt()


if __name__ == "__main__":
    main()