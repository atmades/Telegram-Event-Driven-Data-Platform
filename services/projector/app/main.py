import json
import logging

from confluent_kafka import Consumer

from pydantic import ValidationError
from shared.events import ParsedExpenseEvent

from app.config import settings
from app.db import get_connection_with_retry, insert_expense, truncate_expenses


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


consumer = Consumer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": settings.projector_consumer_group,
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})

def handle_v1_event(conn, event: ParsedExpenseEvent):
    if event.event_type == "expense_recorded":
        insert_expense(conn, event)
        logger.info("Projected expense event_id=%s", event.event_id)
    else:
        logger.info("Skipped event_type=%s", event.event_type)


def main():
    conn = get_connection_with_retry()

    if settings.projector_mode == "replay":
        logger.warning("Projector started in REPLAY mode. Truncating expenses table...")
        truncate_expenses(conn)
        logger.warning("Expenses table truncated")

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

            event_dict = json.loads(msg.value().decode("utf-8"))

            try:
                event = ParsedExpenseEvent.model_validate(event_dict)
            except ValidationError as error:
                logger.error("Invalid parsed event schema: %s", error)
                consumer.commit(msg)
                continue

            version = event.metadata.schema_version

            if version == 1:
                 handle_v1_event(conn, event)
            else:
                logger.warning("Unsupported schema version: %s", version)

            consumer.commit(msg)

    finally:
        consumer.close()
        conn.close()


if __name__ == "__main__":
    main()