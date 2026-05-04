import json
import logging

from confluent_kafka import Consumer, Producer

from app.config import settings
from app.parser import build_parsed_event


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

            raw_event = json.loads(msg.value().decode("utf-8"))
            parsed_event = build_parsed_event(raw_event)

            if parsed_event:
                producer.produce(
                    topic=settings.kafka_parsed_topic,
                    key=parsed_event["event_id"],
                    value=json.dumps(parsed_event).encode("utf-8"),
                    callback=delivery_report,
                )
                producer.poll(0)

                logger.info(
                    "Parsed raw_event_id=%s into event_id=%s",
                    raw_event["event_id"],
                    parsed_event["event_id"],
                )
            else:
                logger.info(
                    "Raw event_id=%s was skipped by parser",
                    raw_event.get("event_id"),
                )

            consumer.commit(msg)

    finally:
        producer.flush(10)
        consumer.close()


if __name__ == "__main__":
    main()