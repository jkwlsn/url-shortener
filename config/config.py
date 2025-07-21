"""Application configuration"""

from pydantic import HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Uses pydantic-settings to import .env variables

    Validates types, raises errors if those without default values are missing"""

    model_config: SettingsConfigDict = SettingsConfigDict(env_file=".env", frozen=True)

    app_name: str = "Jake's URL Shortener"
    base_url: HttpUrl = "https://jkwlsn.dev/"  # type: ignore
    slug_length: int = 7
    max_url_length: int = 2048
    min_url_length: int = 15
    max_url_age: int = 30

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: SecretStr
    postgres_db: str

    @property
    def database_url(self) -> str:
        """Build database connection string and store as a property"""
        return f"postgresql+psycopg_async://{settings.postgres_user}:{settings.postgres_password.get_secret_value()}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"


settings: Settings = Settings()
