import json
import logging

from confluent_kafka import Consumer

from app.config import settings
from app.db import get_connection_with_retry, insert_expense


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


consumer = Consumer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": "expense-projector-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})


def main():
    conn = get_connection_with_retry()

    consumer.subscribe([settings.kafka_parsed_topic])
    logger.info("Expense projector consumer started")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logger.error("Kafka error: %s", msg.error())
                continue

            event = json.loads(msg.value().decode("utf-8"))

            if event.get("event_type") == "expense_recorded":
                insert_expense(conn, event)
                logger.info("Projected expense event_id=%s", event["event_id"])
            else:
                logger.info("Skipped event_type=%s", event.get("event_type"))

            consumer.commit(msg)

    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()