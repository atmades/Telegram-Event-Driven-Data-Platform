from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    postgres_db: str
    postgres_user: str
    postgres_password: str
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    class Config:
        env_file = ".env"


settings = Settings()