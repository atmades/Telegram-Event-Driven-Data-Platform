import re
from datetime import datetime, timezone
from uuid import uuid4

from app.constants import (
    EVENT_TYPE_EXPENSE_RECORDED,
    SOURCE_PARSER,
    SCHEMA_VERSION,
)

from shared.events import ParsedExpenseEvent

def parse_expense_text(text: str) -> dict | None:
    match = re.search(r"(.+?)\s+([\d\s]+(?:[.,]\d+)?)$", text.strip())

    if not match:
        return None

    description = match.group(1).strip()
    raw_amount = match.group(2).replace(" ", "").replace(",", ".")

    try:
        amount = float(raw_amount)
    except ValueError:
        return None

    return {
        "description": description,
        "amount": amount,
        "currency": "ARS",
    }


def build_parsed_event(raw_event: dict) -> ParsedExpenseEvent | None:
    telegram = raw_event.get("telegram", {})
    text = telegram.get("text")

    if not text:
        return None

    parsed = parse_expense_text(text)

    if not parsed:
        return None

    now = datetime.now(timezone.utc)

    return ParsedExpenseEvent(
        event_id=str(uuid4()),
        event_type=EVENT_TYPE_EXPENSE_RECORDED,
        event_time=now,
        source=SOURCE_PARSER,
        raw_event_id=raw_event["event_id"],
        telegram={
            "chat_id": telegram.get("chat_id"),
            "user_id": telegram.get("user_id"),
            "username": telegram.get("username"),
        },
        expense=parsed,
        metadata={
            "schema_version": SCHEMA_VERSION,
            "parsed_at": now,
        },
    )