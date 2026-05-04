import json
import logging
import time

import psycopg2

from app.config import settings


logger = logging.getLogger(__name__)


def get_connection_with_retry(max_attempts: int = 30, delay_seconds: int = 2):
    attempt = 1

    while attempt <= max_attempts:
        try:
            conn = psycopg2.connect(
                dbname=settings.postgres_db,
                user=settings.postgres_user,
                password=settings.postgres_password,
                host=settings.postgres_host,
                port=settings.postgres_port,
            )
            logger.info("Connected to Postgres")
            return conn

        except psycopg2.OperationalError as error:
            logger.warning(
                "Postgres is not ready yet. Attempt %s/%s. Error: %s",
                attempt,
                max_attempts,
                error,
            )
            attempt += 1
            time.sleep(delay_seconds)

    raise RuntimeError("Could not connect to Postgres after retries")


def insert_raw_event(conn, event: dict):
    query = """
        INSERT INTO raw_telegram_events (
            event_id,
            event_type,
            event_time,
            source,
            payload,
            schema_version,
            ingested_at
        )
        VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s)
        ON CONFLICT (event_id) DO NOTHING;
    """

    metadata = event.get("metadata", {})

    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                event["event_id"],
                event["event_type"],
                event["event_time"],
                event["source"],
                json.dumps(event),
                metadata.get("schema_version", 1),
                metadata.get("ingested_at"),
            ),
        )

    conn.commit()