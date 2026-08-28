import json
from datetime import datetime
from pathlib import Path

import duckdb
from kafka import KafkaConsumer


# ============================================================
# CONFIGURATION
# ============================================================

KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "crypto-trades"
CONSUMER_GROUP = "duckdb-consumer-v3"


# Project root = folder containing consumer.py
PROJECT_ROOT = Path(__file__).resolve().parent

DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "crypto.duckdb"


# ============================================================
# DATABASE
# ============================================================

def init_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(DB_PATH))

    conn.execute("""
        CREATE TABLE IF NOT EXISTS raw_crypto_trades (
            timestamp TIMESTAMP,
            symbol VARCHAR,
            price DOUBLE,
            quantity DOUBLE,
            trade_id BIGINT
        )
    """)

    conn.close()


# ============================================================
# CONSUMER
# ============================================================

def main():

    init_database()

    print(f"[CONSUMER] Database: {DB_PATH}")
    print(f"[CONSUMER] Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
    print(f"[CONSUMER] Topic: {KAFKA_TOPIC}")

    conn = duckdb.connect(str(DB_PATH))

    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        group_id=CONSUMER_GROUP,
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
    )

    print("[CONSUMER] Kafka -> DuckDB")
    print("[CONSUMER] Waiting for messages...")

    try:

        for message in consumer:

            trade = message.value

            timestamp = datetime.fromtimestamp(
                trade["timestamp"] / 1000
            )

            conn.execute(
                """
                INSERT INTO raw_crypto_trades
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    timestamp,
                    trade["symbol"],
                    trade["price"],
                    trade["quantity"],
                    trade["trade_id"],
                ],
            )

            print(
                f"[CONSUMER] Saved | "
                f"{trade['symbol']} | "
                f"price={trade['price']} | "
                f"qty={trade['quantity']} | "
                f"trade_id={trade['trade_id']}"
            )

    except KeyboardInterrupt:

        print("\n[CONSUMER] Stopping...")

    finally:

        conn.close()
        consumer.close()

        print("[CONSUMER] Closed.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()