import json
import logging

from confluent_kafka import Consumer, Producer

from app.config import settings
from app.parser import build_parsed_event
from app.constants import DLQ_REASON_PARSE_FAILED
from app.enums import DLQReason


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


consumer = Consumer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "group.id": "parser-consumer",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,
})

producer = Producer({
    "bootstrap.servers": settings.kafka_bootstrap_servers,
    "acks": "all",
    "retries": 3,
    "enable.idempotence": True,
})


def delivery_report(err, msg):
    if err is not None:
        logger.error("Kafka delivery failed: %s", err)
    else:
        logger.info(
            "Parsed event delivered to %s [%s] offset %s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )

def send_to_dlq(raw_event: dict, reason: DLQReason):
    dlq_event = {
        "event_id": raw_event.get("event_id"),
        "source_topic": settings.kafka_raw_topic,
        "error_reason": reason.value,
        "payload": raw_event,
    }

    producer.produce(
        topic=settings.kafka_dlq_topic,
        key=raw_event.get("event_id"),
        value=json.dumps(dlq_event).encode("utf-8"),
        callback=delivery_report,
    )
    producer.poll(0)

    logger.warning(
        "Sent raw_event_id=%s to DLQ. Reason=%s",
        raw_event.get("event_id"),
        reason.value,
    )


def main():
    consumer.subscribe([settings.kafka_raw_topic])
    logger.info("Parser consumer started")

    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                logger.error("Kafka error: %s", msg.error())
                continue

            # --- 1. decode JSON ---
            try:
                raw_event = json.loads(msg.value().decode("utf-8"))
            except Exception:
                send_to_dlq({}, DLQReason.JSON_PARSE_ERROR)
                consumer.commit(msg)
                continue

            # --- 2. parse ---
            try:
                parsed_event = build_parsed_event(raw_event)
            except Exception:
                send_to_dlq(raw_event, DLQReason.UNKNOWN)
                consumer.commit(msg)
                continue

            # --- 3. validation ---
            if not parsed_event:
                send_to_dlq(raw_event, DLQReason.SCHEMA_VALIDATION)
                consumer.commit(msg)
                continue

            # --- 4. produce parsed event ---
            producer.produce(
                topic=settings.kafka_parsed_topic,
                key=parsed_event.event_id,
                value=parsed_event.model_dump_json().encode("utf-8"),
                callback=delivery_report,
            )
            producer.poll(0)

            logger.info(
                "Parsed raw_event_id=%s into event_id=%s",
                raw_event["event_id"],
                parsed_event.event_id,
            )

            consumer.commit(msg)

    finally:
        producer.flush(10)
        consumer.close()


if __name__ == "__main__":
    main()