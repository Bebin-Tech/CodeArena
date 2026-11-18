from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    environment: str = 'development'
    secret_key: str = Field(min_length=32)
    postgres_user: str = 'codearena'
    postgres_password: str
    postgres_db: str = 'codearena'
    postgres_port: int = 5432
    database_url: str | None = None
    redis_url: str = 'redis://127.0.0.1:6379/0'
    frontend_url: str = 'http://127.0.0.1:3000'
    api_url: str = 'http://127.0.0.1:8000'
    smtp_host: str = '127.0.0.1'
    smtp_port: int = 1025
    smtp_username: str = ''
    smtp_password: str = ''
    smtp_starttls: bool = False
    mail_from: str = 'CodeArena <accounts@codearena.local>'
    github_client_id: str = ''
    github_client_secret: str = ''
    session_minutes: int = 60

    @property
    def db_url(self):
        return self.database_url or f'postgresql+psycopg://{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}@127.0.0.1:{self.postgres_port}/{self.postgres_db}'

    @property
    def secure_cookies(self):
        return self.environment == 'production'


@lru_cache
def get_settings():
    return Settings()
