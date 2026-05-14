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


def insert_expense(conn, event):
    query = """
        INSERT INTO expenses (
            expense_id,
            raw_event_id,
            event_time,
            chat_id,
            user_id,
            username,
            description,
            amount,
            currency
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (expense_id) DO NOTHING;
    """

    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                event.event_id,
                event.raw_event_id,
                event.event_time,
                event.telegram.chat_id,
                event.telegram.user_id,
                event.telegram.username,
                event.expense.description,
                event.expense.amount,
                event.expense.currency,
            ),
        )

    conn.commit()

## Clean projection table
def truncate_expenses(conn):
    with conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE expenses;")

    conn.commit()