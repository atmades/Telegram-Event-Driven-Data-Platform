from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_parsed_topic: str = "telegram.parsed_events"

    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    projector_mode: str = "normal"
    projector_consumer_group: str = "expense-projector-consumer"

    class Config:
        env_file = ".env"


settings = Settings()