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


CREATE TABLE IF NOT EXISTS expenses (
    expense_id UUID PRIMARY KEY,
    raw_event_id UUID NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    chat_id BIGINT,
    user_id BIGINT,
    username TEXT,
    description TEXT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_expenses_raw_event_id
ON expenses(raw_event_id);