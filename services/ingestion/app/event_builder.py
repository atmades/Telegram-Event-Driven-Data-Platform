from datetime import datetime, timezone
from uuid import uuid4


def build_telegram_message_event(message) -> dict:
    now = datetime.now(timezone.utc)

    return {
        "event_id": str(uuid4()),
        "event_type": "telegram_message_created",
        "event_time": now.isoformat(),
        "source": "telegram",
        "telegram": {
            "chat_id": message.chat_id,
            "message_id": message.message_id,
            "user_id": message.from_user.id if message.from_user else None,
            "username": message.from_user.username if message.from_user else None,
            "first_name": message.from_user.first_name if message.from_user else None,
            "text": message.text,
        },
        "metadata": {
            "schema_version": 1,
            "ingested_at": now.isoformat(),
        },
    }