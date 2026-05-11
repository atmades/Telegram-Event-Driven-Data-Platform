

# Reliability

## Goals

- No data loss
- Safe retries
- Graceful handling of invalid data
- Deterministic processing

## Producer Reliability

Kafka producers are configured with:

- `acks=all`
- `retries=3`
- `enable.idempotence=true`

This ensures:
- messages are acknowledged by Kafka
- retries do not create duplicates

## Consumer Reliability

Consumers:
- manually commit offsets
- only commit after successful processing

This ensures:
- no message loss
- safe reprocessing on failure

## Idempotency

Database writes use:

```sql
PRIMARY KEY (event_id)
```
and:

```
ON CONFLICT DO NOTHING
```

## Dead Letter Queue (DLQ)

Invalid or unprocessable events are sent to:

```
telegram.dlq
```

### Reasons include:

- JSON decode failure
- schema validation failure
- unexpected runtime error

### DLQ enables:

- debugging
- replay
- monitoring data quality
- Replay Capability

### Because Kafka stores events:

- consumers can restart
- projections can be rebuilt
- system state can be recomputed

### Failure Scenarios

```mermaid
flowchart TD

A[Incoming Event] --> B{JSON Decode OK?}

B -- No --> DLQ1[DLQ: json_decode_failed]

B -- Yes --> C{Parsing OK?}

C -- No --> DLQ2[DLQ: schema_validation_failed]

C -- Yes --> D[Produce Parsed Event]

D --> E{Kafka Available?}

E -- No --> Retry1[Producer Retries]

E -- Yes --> F[Parsed Event Stored in Kafka]

F --> G[Projector Consumer]

G --> H{DB Write OK?}

H -- No --> Retry2[Retry on Restart]

H -- Yes --> I[Projection Updated]

```


### Graceful Shutdown
- ingestion flushes Kafka producer
- consumers commit offsets before exit