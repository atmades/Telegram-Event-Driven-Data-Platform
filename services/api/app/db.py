import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import settings


def get_connection():
    return psycopg2.connect(
        dbname=settings.postgres_db,
        user=settings.postgres_user,
        password=settings.postgres_password,
        host=settings.postgres_host,
        port=settings.postgres_port,
        cursor_factory=RealDictCursor,
    )


def fetch_expenses(limit: int = 20):
    query = """
        SELECT
            expense_id,
            raw_event_id,
            event_time,
            chat_id,
            user_id,
            username,
            description,
            amount,
            currency,
            created_at
        FROM expenses
        ORDER BY created_at DESC
        LIMIT %s;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            return cur.fetchall()


def fetch_expenses_summary():
    query = """
        SELECT
            currency,
            COUNT(*) AS expense_count,
            SUM(amount) AS total_amount
        FROM expenses
        GROUP BY currency
        ORDER BY currency;
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            return cur.fetchall()