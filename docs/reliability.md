

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
    subgraph RESILIENCE [🛡️ Failure & Recovery Patterns]
        P1[🔴 Parser Failure] --> P2[⚠️ Invalid data / logic error]
        P2 --> P3[📤 Route to DLQ]
        P3 --> P4[✅ Consumer continues processing]

        D1[🟠 Database Failure] --> D2[⚠️ Write timeout / connection loss]
        D2 --> D3[🔄 Consumer crashes / stops]
        D3 --> D4[✅ Auto-retry on restart via committed offset]

        K1[🟡 Kafka Unavailable] --> K2[⚠️ Broker down / network issue]
        K2 --> K3[🔁 Producer internal retries]
        K3 --> K4[✅ Idempotent delivery guaranteed]
    end

    classDef title fill:#f8f9fa,stroke:#adb5bd,stroke-width:2px;
    classDef error fill:#ffebee,stroke:#c62828,stroke-width:2px;
    classDef action fill:#fff3e0,stroke:#ef6c00,stroke-width:2px;
    classDef success fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;

    class P1,D1,K1 title;
    class P2,D2,K2 error;
    class P3,D3,K3 action;
    class P4,D4,K4 success;
    
  ```


### Graceful Shutdown
- ingestion flushes Kafka producer
- consumers commit offsets before exit