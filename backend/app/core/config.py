from functools import lru_cache
import os
from pathlib import Path
from urllib.parse import quote_plus

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[3]


def public_url():
    domain = os.environ.get('VERCEL_PROJECT_PRODUCTION_URL')
    return f'https://{domain}' if domain else 'http://127.0.0.1:3000'


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT / '.env', extra='ignore')
    environment: str = 'development'
    secret_key: str = Field(min_length=32)
    postgres_user: str = 'codearena'
    postgres_password: str = ''
    postgres_db: str = 'codearena'
    postgres_port: int = 5432
    database_url: str | None = None
    redis_url: str = Field(default='redis://127.0.0.1:6379/0', validation_alias=AliasChoices('REDIS_URL', 'KV_URL'))
    frontend_url: str = Field(default_factory=public_url)
    api_url: str = Field(default_factory=lambda: public_url() if os.environ.get('VERCEL') else 'http://127.0.0.1:8000')
    smtp_host: str = '127.0.0.1'
    smtp_port: int = 1025
    smtp_username: str = ''
    smtp_password: str = Field(default='', validation_alias=AliasChoices('SMTP_PASSWORD', 'RESEND_API_KEY'))
    smtp_starttls: bool = False
    mail_from: str = 'CodeArena <accounts@codearena.local>'
    github_client_id: str = ''
    github_client_secret: str = ''
    session_minutes: int = 60

    @model_validator(mode='after')
    def require_database(self):
        if not self.database_url and not self.postgres_password:
            raise ValueError('Configure DATABASE_URL or POSTGRES_PASSWORD.')
        return self

    @property
    def db_url(self):
        if self.database_url:
            # Neon provides standard PostgreSQL URLs; explicitly select psycopg 3.
            for prefix in ('postgres://', 'postgresql://'):
                if self.database_url.startswith(prefix):
                    return 'postgresql+psycopg://' + self.database_url[len(prefix):]
            return self.database_url
        return f'postgresql+psycopg://{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}@127.0.0.1:{self.postgres_port}/{self.postgres_db}'

    @property
    def secure_cookies(self):
        return self.environment == 'production'


@lru_cache
def get_settings():
    return Settings()
