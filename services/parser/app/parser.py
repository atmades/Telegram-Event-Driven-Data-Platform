import re
from datetime import datetime, timezone
from uuid import uuid4

from app.constants import (
    EVENT_TYPE_EXPENSE_RECORDED,
    SOURCE_PARSER,
    SCHEMA_VERSION,
)


def parse_expense_text(text: str) -> dict | None:
    match = re.search(r"(.+?)\s+(\d+(?:[.,]\d+)?)$", text.strip())

    if not match:
        return None

    description = match.group(1).strip()
    amount = float(match.group(2).replace(",", "."))

    return {
        "description": description,
        "amount": amount,
        "currency": "ARS",
    }


def build_parsed_event(raw_event: dict) -> dict | None:
    telegram = raw_event.get("telegram", {})
    text = telegram.get("text")

    if not text:
        return None

    parsed = parse_expense_text(text)

    if not parsed:
        return None

    now = datetime.now(timezone.utc)

    return {
        "event_id": str(uuid4()),
        "event_type": EVENT_TYPE_EXPENSE_RECORDED,
        "event_time": now.isoformat(),
        "source": SOURCE_PARSER,
        "raw_event_id": raw_event["event_id"],
        "telegram": {
            "chat_id": telegram.get("chat_id"),
            "user_id": telegram.get("user_id"),
            "username": telegram.get("username"),
        },
        "expense": parsed,
        "metadata": {
            "schema_version": SCHEMA_VERSION,
            "parsed_at": now.isoformat(),
        },
    }