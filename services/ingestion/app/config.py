from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    telegram_bot_token: str
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_raw_topic: str = "telegram.raw_events"

    class Config:
        env_file = ".env"


settings = Settings()