import json
import logging

from confluent_kafka import Producer
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

from app.config import settings
from app.event_builder import build_telegram_message_event

logging.basicConfig(level=logging.INFO)

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.getLogger("apscheduler").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

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
            "Event delivered to %s [%s] offset %s",
            msg.topic(),
            msg.partition(),
            msg.offset(),
        )


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    event = build_telegram_message_event(update.message)

    producer.produce(
        topic=settings.kafka_raw_topic,
        key=event["event_id"],
        value=json.dumps(event).encode("utf-8"),
        callback=delivery_report,
    )
    producer.poll(0)

    logger.info("Produced event_id=%s", event["event_id"])


async def on_shutdown(application):
    logger.info("Shutting down ingestion service...")
    producer.flush(10)
    logger.info("Kafka producer flushed")


def main():
    app = (
        ApplicationBuilder()
        .token(settings.telegram_bot_token)
        .post_shutdown(on_shutdown)
        .build()
    )

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Telegram ingestion service started")
    app.run_polling()


if __name__ == "__main__":
    main()