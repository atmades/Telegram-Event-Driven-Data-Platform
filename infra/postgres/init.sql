CREATE TABLE IF NOT EXISTS raw_telegram_events (
    event_id UUID PRIMARY KEY,
    event_type TEXT NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    source TEXT NOT NULL,
    payload JSONB NOT NULL,
    schema_version INT NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_raw_telegram_events_event_time
ON raw_telegram_events(event_time);