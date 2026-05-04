import json
import logging

from confluent_kafka import Consumer

from app.config import settings
from app.db import get_connection_with_retry, insert_raw_event


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


consumer = Consumer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": "raw-writer-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})


def main():
    conn = get_connection_with_retry()

    consumer.subscribe([settings.kafka_raw_topic])
    logger.info("Raw writer consumer started")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logger.error("Kafka error: %s", msg.error())
                continue

            event = json.loads(msg.value().decode("utf-8"))

            insert_raw_event(conn, event)
            consumer.commit(msg)

            logger.info("Saved raw event_id=%s", event["event_id"])

    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()