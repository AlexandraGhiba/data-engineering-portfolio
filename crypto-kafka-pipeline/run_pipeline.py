import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VENV_PYTHON = ROOT / ".venv" / "Scripts" / "python.exe"
DBT = ROOT / ".venv" / "Scripts" / "dbt.exe"
DBT_PROJECT = ROOT / "dbt_crypto"


def run_dbt():
    print("\n" + "=" * 60)
    print("[PIPELINE] Running dbt build (models + tests)...")
    print("=" * 60)

    result = subprocess.run(
        [
            str(DBT),
            "build",
            "--project-dir",
            str(DBT_PROJECT),
            "--profiles-dir",
            str(DBT_PROJECT),
        ],
        cwd=DBT_PROJECT,
    )

    if result.returncode != 0:
        raise RuntimeError("dbt build failed")

    print("\n[PIPELINE] dbt models and tests completed successfully.")


def stop_process(process, name):
    if process.poll() is None:
        print(f"[PIPELINE] Stopping {name}...")
        process.terminate()

        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            print(f"[PIPELINE] {name} did not stop. Killing process...")
            process.kill()
            process.wait()


def main():
    print("=" * 60)
    print("CRYPTO STREAMING PIPELINE")
    print("=" * 60)

    producer = None
    consumer = None

    try:
        print("\n[PIPELINE] Starting producer...")
        producer = subprocess.Popen(
            [str(VENV_PYTHON), str(ROOT / "producer.py")],
            cwd=ROOT,
        )

        print("[PIPELINE] Starting consumer...")
        consumer = subprocess.Popen(
            [str(VENV_PYTHON), str(ROOT / "consumer.py")],
            cwd=ROOT,
        )

        print("[PIPELINE] Producer started.")
        print("[PIPELINE] Consumer started.")
        print("\n[PIPELINE] Streaming... Press CTRL+C to stop.\n")

        while True:
            # Detect if one of the streaming processes crashes
            if producer.poll() is not None:
                raise RuntimeError(
                    f"Producer stopped unexpectedly "
                    f"(exit code {producer.returncode})"
                )

            if consumer.poll() is not None:
                raise RuntimeError(
                    f"Consumer stopped unexpectedly "
                    f"(exit code {consumer.returncode})"
                )

            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\n[PIPELINE] CTRL+C received.")

    finally:
        print("\n[PIPELINE] Stopping streaming services...")

        if producer is not None:
            stop_process(producer, "producer")

        if consumer is not None:
            stop_process(consumer, "consumer")

        print("[PIPELINE] Streaming stopped.")

    # Only starts after producer + consumer are stopped
    run_dbt()

    print("\n" + "=" * 60)
    print("[PIPELINE] PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    main()