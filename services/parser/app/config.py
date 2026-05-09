from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_raw_topic: str = "telegram.raw_events"
    kafka_parsed_topic: str = "telegram.parsed_events"
    kafka_dlq_topic: str = "telegram.dlq"

    class Config:
        env_file = ".env"


settings = Settings()