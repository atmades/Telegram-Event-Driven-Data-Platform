# Event Model

## Philosophy

Events represent immutable facts that happened in the system.

- Events are append-only
- Events are never updated or deleted
- All state is derived from events

## Raw Event

Topic: `telegram.raw_events`

```json
{
  "event_id": "uuid",
  "event_type": "telegram_message_created",
  "event_time": "timestamp",
  "source": "telegram",
  "telegram": {
    "chat_id": 123,
    "user_id": 456,
    "username": "user",
    "text": "coffee 3500"
  },
  "metadata": {
    "schema_version": 1,
    "ingested_at": "timestamp"
  }
}

```
## Parsed Event

Topic: telegram.parsed_events
```json
{
  "event_id": "uuid",
  "event_type": "expense_recorded",
  "event_time": "timestamp",
  "source": "parser",
  "raw_event_id": "uuid",
  "telegram": {
    "chat_id": 123,
    "user_id": 456,
    "username": "user"
  },
  "expense": {
    "description": "coffee",
    "amount": 3500,
    "currency": "ARS"
  },
  "metadata": {
    "schema_version": 1,
    "parsed_at": "timestamp"
  }
}
```
## DLQ Event

Topic: telegram.dlq

```
{
  "event_id": "uuid",
  "source_topic": "telegram.raw_events",
  "error_reason": "schema_validation_failed",
  "payload": { ...original event... }
}
```

## Event Evolution

Events are versioned using:

```
metadata.schema_version
```

Future changes should:

- preserve backward compatibility
- avoid breaking consumers

## Idempotency

Each event has a unique:

```
event_id
```
