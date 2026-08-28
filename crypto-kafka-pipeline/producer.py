import asyncio
import json

import websockets
from kafka import KafkaProducer


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "crypto-trades"

BINANCE_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"


producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


async def main():
    print("[PRODUCER] Connecting to Binance...")

    async with websockets.connect(BINANCE_URL) as websocket:
        print("[PRODUCER] Connected!")
        print("[PRODUCER] Binance -> Kafka")
        print("[PRODUCER] Press CTRL+C to stop.")

        while True:
            message = await websocket.recv()
            data = json.loads(message)

            trade = {
                "timestamp": data["T"],
                "symbol": data["s"],
                "price": float(data["p"]),
                "quantity": float(data["q"]),
                "trade_id": data["t"],
            }

            producer.send(
                KAFKA_TOPIC,
                key=trade["symbol"].encode("utf-8"),
                value=trade,
            )

            print(
                f"[PRODUCER] {trade['symbol']} | "
                f" | "
                f"qty={trade['quantity']} | "
                f"id={trade['trade_id']}"
            )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[PRODUCER] Stopped.")
    finally:
        producer.flush()
        producer.close()
